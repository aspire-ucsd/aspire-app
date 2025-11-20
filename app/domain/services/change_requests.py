from typing import List, Union, Literal, Tuple
import logging
from fastapi import Depends
from datetime import datetime, timedelta, time, UTC
import pytz
import os
import json

from app.app.errors.validation_error import ValidationError

from app.domain.models.session import SessionExtended
from app.domain.models.change_requests import (
    ChangeRequestRead, ChangeRequestCreateClient,
    ChangeRequestUpdate, ChangeRequestCreate,
    Comment, EntityTypeEnum,
    ModificationTypeEnum,
)
from app.domain.protocols.services.change_requests import ChangeRequestService as ChangeRequestServiceProtocol
from app.domain.protocols.repositories.change_request import ChangeRequestRepository as ChangeRequestRepoProtocol
from app.infrastructure.database.repositories.change_requests import ChangeRequestRepository

from app.infrastructure.database.repositories.course import CourseRepository
from app.domain.protocols.repositories.course import CourseRepository as CourseRepoProtocol

from app.domain.services.concept import ConceptService
from app.domain.models.concept import (
    ConceptCreate, ConceptToCollectionCreate,
    ConceptToConceptCreate, ConceptToConceptDelete,
)

from app.infrastructure.database.repositories.client import ClientRepository
from app.domain.protocols.repositories.client import ClientRepository as ClientRepositoryProtocol

from app.domain.services.concept_collection import CollectionService
from app.domain.protocols.services.concept_collection import CollectionService as CollectionServiceProtocol
from app.domain.protocols.services.concept import (
    ConceptService as ConceptServiceProtocol,
    ConceptToModuleService as CToCcServiceProtocol,
    ConceptToConceptService as CToCServiceProtocol
)

from app.config.environment import get_settings

logger = logging.getLogger(__name__)
_SETTINGS = get_settings()

class ChangeRequestService(ChangeRequestServiceProtocol):
    def __init__(
        self, 
        validation_queue_repo: ChangeRequestRepoProtocol = Depends(ChangeRequestRepository),
        course_repo: CourseRepoProtocol = Depends(CourseRepository),
        # TODO: Add Course Service and CToC Service.
        concept_repo: Union[
            ConceptServiceProtocol, CToCcServiceProtocol, CToCServiceProtocol
        ] = Depends(ConceptService),
        collections_repo: CollectionServiceProtocol = Depends(CollectionService),
        client_repo: ClientRepositoryProtocol = Depends(ClientRepository)

    ):
        self.validation_queue_repo = validation_queue_repo
        self.course_repo = course_repo
        self.concept_repo = concept_repo
        self.client_repo = client_repo

    async def get_reviewers(self, item: ChangeRequestCreateClient, client_id: int) -> List[int]:
        return await self.client_repo.get_reviewers(item=item, client_id=client_id)

    async def get_next_voting_time(self):
        """
        Voting times always end at 12:00pm or 5:00pm in the timezone specified in the environment, 
        this function selects the soonest option that is greater than 2 hours from time of request and converts the result to UTC.
        """

        noon_time = time(12, 0)  # 12:00pm
        evening_time = time(17, 0)  # 5:00pm
        
        local_tz = pytz.timezone(_SETTINGS.TIMEZONE)
        
        now_local = datetime.now(local_tz)
        
        today_noon = local_tz.localize(datetime.combine(now_local.date(), noon_time))
        today_evening = local_tz.localize(datetime.combine(now_local.date(), evening_time))
        tomorrow_noon = local_tz.localize(datetime.combine(now_local.date() + timedelta(days=1), noon_time))

        time_until_noon = (today_noon - now_local).total_seconds()
        time_until_evening = (today_evening - now_local).total_seconds()
        
        
        threshold = 2 * 60 * 60  # 2 hours in seconds

        if 0 <= time_until_noon < threshold:
            # If less than 2 hours until noon, schedule for 5:00pm
            next_schedule = today_evening

        elif 0 <= time_until_evening < threshold or time_until_evening < 0 > time_until_noon:
            # If less than 2 hours until evening, or past evening, schedule for 12:00pm the next day
            next_schedule = tomorrow_noon

        else:
            # Otherwise, schedule for the nearest time (noon or evening) today
            next_schedule = today_noon if now_local < today_noon else today_evening

        # Converts back to UTC for consistent storage and later reconversion
        next_schedule_utc = next_schedule.astimezone(pytz.utc)
        
        return next_schedule_utc

    async def get_vote_params(self, entity_type: str, modification_type: str):
        match entity_type:
            case "concept":
                if modification_type == "update":
                    vote_time = await self.get_next_voting_time()
                    return "simple_majority", vote_time
                
                if modification_type == "delete":
                    vote_time = await self.get_next_voting_time()
                    return "veto", vote_time
                
                return None, None
            
            case "concept_to_concept":
                vote_time = await self.get_next_voting_time()
                return "simple_majority", vote_time

            case "question":
                if modification_type == "delete":
                    vote_time = await self.get_next_voting_time()
                    return "veto", vote_time
                
                else:
                    vote_time = await self.get_next_voting_time()
                    return "simple_majority", vote_time

            case "answer":
                vote_time = await self.get_next_voting_time()
                return "simple_majority", vote_time
    

    async def add_item(self, item: ChangeRequestCreateClient, client_session: SessionExtended) -> ChangeRequestRead:
        client_id = client_session.user_credentials.internal_id
        reviewers = []
        # Reviewers are only required for pending CRs
        if item.validation_status == "pending":
            reviewers = await self.get_reviewers(
                item=item,
                client_id=client_id
                )
        
        vote_type, closes_at = await self.get_vote_params(entity_type=item.entity_type, modification_type=item.modification_type)
        # Drafts and changes without additional reviewers dont need a close time
        if item.validation_status == 'draft' or len(reviewers) < 2:
            closes_at = None

        full_create_obj = ChangeRequestCreate(
            **item.model_dump(), 
            submitted_by=client_id,
            reviewers=reviewers,
            vote_type=vote_type,
            closes_at=closes_at,
            )
        
        return await self.validation_queue_repo.add(item=full_create_obj)
    

    async def bulk_add_items(self, items: List[ChangeRequestCreateClient], client_session: SessionExtended) -> List[ChangeRequestRead]:
        completed_validation_items = []
        client_id = client_session.user_credentials.internal_id

        for item in items:
            reviewers = []
            # Reviewers are only required for pending CRs
            if item.validation_status == "pending":
                reviewers = await self.get_reviewers(
                    entity_type=item.entity_type, 
                    user_filter=item.user_filters,
                    client_id=client_id
                    )
            
            vote_type, closes_at = await self.get_vote_params(entity_type=item.entity_type, modification_type=item.modification_type)
            # Drafts dont need a close time
            if item.validation_status == 'draft':
                closes_at = None

            full_create_obj = ChangeRequestCreate(
                **item.model_dump(), 
                submitted_by=client_id,
                reviewers=reviewers,
                vote_type=vote_type,
                closes_at=closes_at,
                )
            
            completed_validation_items.append(full_create_obj)

        return await self.validation_queue_repo.bulk_add(items=completed_validation_items)
    

    async def update_item(
            self, 
            update: ChangeRequestUpdate, 
        )-> ChangeRequestRead:
        return await self.validation_queue_repo.update(update=update, apply_null_closes_at=False)

    async def close_request(
        self,
        change_request_id: int,
        client_session: SessionExtended
    ) -> ChangeRequestRead:
        return await self.validation_queue_repo.close_request(change_request_id=change_request_id, client_session=client_session)

    async def get_relevant_items(self, client_session: SessionExtended) -> Union[List[ChangeRequestRead], list]:
        return await self.validation_queue_repo.get_related(client_id=client_session.user_credentials.internal_id)
    
    async def get_my_closed_requests(self, client_session: SessionExtended)-> Union[List[ChangeRequestRead], list]:
        return await self.validation_queue_repo.get_my_closed(client_id=client_session.user_credentials.internal_id)
    
    async def get_my_drafts(self, client_session: SessionExtended)-> Union[List[ChangeRequestRead], list]:
        return await self.validation_queue_repo.get_my_drafts(client_id=client_session.user_credentials.internal_id)
    
    async def delete_draft(        
        self,
        client_session: SessionExtended, 
        change_request_id: int 
    ) -> None:
        return await self.validation_queue_repo.delete_draft(client_session=client_session, change_request_id=change_request_id)

    async def on_approval_procedure(
            self,
            client_session: SessionExtended,
            change_request: ChangeRequestRead
    ) -> Tuple[bool, Union[None, Comment]]:
        """ This function deals with the procedure of approving a Change Request.

        Notes:
            Currently, the scenarios dealt with in this function are:
            - Approval of a Concept
            - Update of a Concept.
            - Addition of a Concept to Concept Junction
            - Update of a Concept to Concept Junction

        Args:
            client_session: Client Session
            change_request: Change Request Object Read from the DB

        Returns:
            Comment Object
        """
        match change_request.entity_type:

            case EntityTypeEnum.concept:
                # Create, Update, and Delete operations supported by Concept.
                try:
                    match change_request.modification_type:
                        case ModificationTypeEnum.create:
                            await self.concept_repo.create_concept(
                                concept=ConceptCreate(
                                    name=change_request.entity_data["name"],
                                    subject=change_request.entity_data["subject"],
                                    difficulty=change_request.entity_data["difficulty"],
                                    summary= change_request.entity_data["summary"] if
                                    change_request.entity_data["summary"] else None
                                )
                            )

                        case ModificationTypeEnum.update:
                            await self.concept_repo.update_one_concept(
                                concept_name=change_request.entity_id,
                                updated_concept=ConceptCreate(
                                    name=change_request.entity_data["name"],
                                    subject=change_request.entity_data["subject"],
                                    difficulty=change_request.entity_data["difficulty"],
                                    summary=change_request.entity_data["summary"] if
                                    change_request.entity_data["summary"] else None
                                )
                            )

                        case ModificationTypeEnum.delete:
                            await self.concept_repo.delete_one_concept(
                                concept_name=change_request.entity_data["name"]
                            )

                    if change_request.post_approval_procedure:
                        if change_request.post_approval_procedure["type"] == "junction":
                            # This try catch lets the promotion procedure fail gracefully.
                            try:
                                await self.concept_repo.create_module_junction(
                                    ConceptToCollectionCreate(
                                        concept_name=change_request.entity_data['name'],
                                        collection_id=change_request.post_approval_procedure["target_id"]
                                    )
                                )
                                return (
                                    True,
                                    Comment(
                                        type='update',
                                        content=f"msg|Concept '{change_request.entity_data['name']}' "
                                                f"linked to entity: "
                                                f"{change_request.post_approval_procedure['target_table']} {change_request.post_approval_procedure['target_id']}."
                                                f"|data_type|ConceptRead|data"
                                                f"|{json.dumps(change_request.entity_data)}",
                                        submitted_by=client_session.user_credentials.internal_id
                                    )
                                )
                            except Exception as err:
                                return (
                                    True,
                                    Comment(
                                        type='update',
                                        content=f"msg|Concept '{change_request.entity_data['name']}' "
                                                f"could NOT be linked to entity. Error: {err}"
                                                f"|data_type|ConceptRead|data"
                                                f"|{json.dumps(change_request.entity_data)}",
                                        submitted_by=client_session.user_credentials.internal_id
                                    )
                                )
                    return True, None

                except Exception as err:
                    logger.exception(msg=f"Failed to process ChangeRequest for "
                                        f"{json.dumps(change_request.entity_data)}. We get the "
                                        f"following error: {err} ")
                    return (
                        False,
                        Comment(
                            type='update',
                            content=f"msg|Concept '{change_request.entity_data['name']}' could "
                                    f"not be processed. Failed due to error: {err}. "
                                    f"|data_type|ConceptRead|data"
                                    f"|{json.dumps(change_request.entity_data)}",
                            submitted_by=client_session.user_credentials.internal_id
                        )
                    )

            case EntityTypeEnum.concept_to_concept:
                # Only Create and Delete operations supported by Concept To Concept.
                try:
                    match change_request.modification_type:
                        case ModificationTypeEnum.create:
                            await self.concept_repo.create_concept_junction(
                                junction=ConceptToConceptCreate(
                                    concept_name=change_request.entity_data["concept_name"],
                                    prereq_name=change_request.entity_data["prereq_name"]
                                )
                            )

                        case ModificationTypeEnum.update:
                            # This is an invalid operation as based on discussion held on 12/12/24,
                            # in the current design it does not make sense to update a
                            # concept_to_concept relation. An add or delete should suffice.
                            return (
                                False,
                                Comment(
                                    type='update',
                                    content=f"msg|Concept '{change_request.entity_data['concept_name']}' "
                                            f"could not be processed. Invalid request: Concept To "
                                            f"Concept Relations do not support update operations. "
                                            f"|data_type|ConceptToConceptRead|data"
                                            f"|{json.dumps(change_request.entity_data)}",
                                    submitted_by=client_session.user_credentials.internal_id
                                )
                            )

                        case ModificationTypeEnum.delete:
                            await self.concept_repo.delete_junctions(
                                junctions=[
                                    ConceptToConceptDelete(
                                        concept_name=change_request.entity_data["concept_name"],
                                        prereq_name=change_request.entity_data["prereq_name"]
                                    )
                                ]
                            )

                    return True, None

                except Exception as err:
                    logger.exception(msg=f"Failed to process ChangeRequest for "
                                        f"{json.dumps(change_request.entity_data)}. We get the "
                                        f"following error: {err} ")
                    return (
                        False,
                        Comment(
                            type='update',
                            content=f"msg|Concept To Concept change request could "
                                    f"not be processed. Failed due to error: {err}. "
                                    f"|data_type|ConceptToConceptRead|data"
                                    f"|{json.dumps(change_request.entity_data)}",
                            submitted_by=client_session.user_credentials.internal_id
                        )
                    )

            case EntityTypeEnum.question:
                return (
                    False,
                    Comment(
                        type='update',
                        content=f"msg| This ChangeRequest EntityType is currently not supported."
                                f"|data_type|None"
                                f"|data|None",
                        submitted_by=client_session.user_credentials.internal_id
                    )
                )

            case EntityTypeEnum.answer:
                return (
                    False,
                    Comment(
                        type='update',
                        content=f"msg| This ChangeRequest EntityType is currently not supported."
                                f"|data_type|None"
                                f"|data|None",
                        submitted_by=client_session.user_credentials.internal_id
                    )
                )
        return (
            False,
            Comment(
                type='update',
                content=f"msg| This ChangeRequest EntityType is Invalid. "
                        f"EntityType: {change_request.entity_type}"
                        f"|data_type|None"
                        f"|data|None",
                submitted_by=client_session.user_credentials.internal_id
            )
        )

    async def update_status(
        self,
        client_session: SessionExtended, 
        change_request_id: int, 
        status: Literal["pending", "approved", "rejected", "draft"] = "pending"
    ) -> ChangeRequestRead:
        """
        Updates the validation status of a change request, additional changes or actions required upon changing validation status are automatically applied.
        In all cases votes are reset and a comment noting the status update and prior vote is added.


        Updating a CR to 'pending' automatically assigns reviewers, and a closing time.

        Updating a CR to 'draft' automatically clears all reviewers and the closing time.

        Updating a CR to 'approved' checks if approval is allowed, if yes it automatically promotes the CR to the db, adds the reviewer and commit time, and clears all reviewers and the closing time.

        Updating a CR to 'rejected' clears all reviewers and the closing time, adds the commit time.

        :raises ValidationError: The requested status conflicts with the state of the Change Request.
            (Ex. User requests to approve a CR where a required simple majority vote resulted in only 33% approval.) 
        """
        
        change_request_old: ChangeRequestRead = await self.validation_queue_repo.get_one(change_request_id=change_request_id)

        # ! Approving a CR requires additional checks due to the voting system, raises ValidationError when the state of the CR conflicts with the ability to be approved
        if status == 'approved' and change_request_old.vote_type:
            # * Prevents approval if the vote has not concluded
            if change_request_old.closes_at and datetime.strptime(change_request_old.closes_at, '%Y-%m-%d %H:%M:%S %Z').astimezone(UTC) > datetime.now(UTC):
                raise ValidationError(
                    origin="ChangeRequestService.update_status",
                    status_code=409,
                    message="Change Requests with vote cannot be approved prior to closing time"
                    )
            vote_count = len(change_request_old.votes)
            approved_count = change_request_old.votes.count('approved')
            rejected_count = change_request_old.votes.count('rejected')

            # TODO: Enable minimum vote count check when the number of users grows
            # if vote_count <= 0:
            #     raise ValidationError(
            #         origin="ChangeRequestService.update_status",
            #         status_code=409,
            #         message="Change Requests requiring public review cannot be approved without any votes"
            #         )
            
            # * Veto votes automatically reject the CR when the vote is cast, however an additional check is provided here for added enforcement
            if change_request_old.vote_type == 'veto' and rejected_count > 0:
                raise ValidationError(
                    origin="ChangeRequestService.update_status",
                    status_code=409,
                    message="Change Requests with vote set to 'veto' cannot be approved without unanimous support"
                    )
            
            # * Simple majority votes must have more approved votes than rejected votes, ties default to rejected
            if change_request_old.vote_type == 'simple_majority' and rejected_count > approved_count:
                raise ValidationError(
                    origin="ChangeRequestService.update_status",
                    status_code=409,
                    message=f"Change Requests with vote set to 'simple_majority' cannot be approved without support > 50%.\
                        This Change Request only received {approved_count / vote_count * 100}% approval"
                    )

        # Votes, reviewers, and closing time are reset by default to their default values, may be overridden by different status values
        change_update = ChangeRequestUpdate(
            id=change_request_id, 
            votes=[], 
            validation_status=status, 
            reviewers=[]
            )

        match status:
            # Always adds a comment noting the status update and any prior votes
            case 'pending':
                # Updating a CR to 'pending' automatically assigns reviewers, and a closing time.
                update_comment = Comment(
                    type='update', 
                    content=f"msg|Status changed to 'pending'",
                    submitted_by=client_session.user_credentials.internal_id
                    )
                change_update.comments = [update_comment]

                reviewers = await self.get_reviewers(
                    item=change_request_old,
                    client_id=client_session.user_credentials.internal_id
                    )
                # Reviewers will always contain at least the id of the client, if there are no additional reviewers identified there is no need to review and the request can simply close.
                if len(reviewers) < 2:
                    closes_at = None
                    no_reviewer_comment = Comment(
                    type='update', 
                    content="msg|No reviewers found - Request available for approval.",
                    submitted_by=client_session.user_credentials.internal_id
                    )
                    change_update.comments.append(no_reviewer_comment)

                else:
                    closes_at = await self.get_next_voting_time()
                    has_reviewers_comment = Comment(
                    type='update', 
                    content=f"msg|System assigned {len(reviewers)} reviewers to this Change Request - {'Reviewers may veto Change Requests of this type for the duration of the review.' if change_request_old.vote_type == 'veto' else 'Reviewers must vote on Change Requests of this type, majority consensus is required.' if change_request_old.vote_type == 'simple_majority' else 'Review requested by submitter, vote results not enforced.'}",
                    submitted_by=client_session.user_credentials.internal_id
                    )
                    change_update.comments.append(has_reviewers_comment)

                change_update.votes = None
                change_update.closes_at = closes_at
                change_update.reviewers = reviewers

            case 'draft':
                # Updating a CR to 'draft' does nothing extra.
                update_comment = Comment(
                    type='update', 
                    content=f"msg|Status changed to 'draft'",
                    submitted_by=client_session.user_credentials.internal_id
                    )
                change_update.comments = [update_comment]
                

            case 'approved':
                # Updating a CR to 'approved' automatically promotes the CR to the db, and adds the reviewed_by and committed_at time to the CR.
                # TODO: Perform checks on CR ownership and whether an approval is valid
                # TODO: Create router for promoting change requests to db
                comment_list = []

                status_flag, comment = await self.on_approval_procedure(
                    client_session=client_session,
                    change_request=change_request_old
                )
                if comment:
                    comment_list.append(comment)

                if status_flag:
                    comment_list.append(
                        Comment(
                            type='update',
                            content=f"msg|Status changed to 'approved'|data_type|votes|data|{json.dumps(change_request_old.votes)}",
                            submitted_by=client_session.user_credentials.internal_id
                        )
                    )
                else:
                    change_update.validation_status = 'rejected'
                    comment_list.append(
                        Comment(
                            type='update',
                            content=f"msg|Status changed to 'rejected'. Due to error encountered "
                                    f"during processing."
                                    f"|data_type|votes"
                                    f"|data|{json.dumps(change_request_old.votes)}",
                            submitted_by=client_session.user_credentials.internal_id
                        )
                    )

                change_update.comments = comment_list
                change_update.reviewed_by = client_session.user_credentials.internal_id
                change_update.committed_at = datetime.now(UTC)

                
            case 'rejected':
                # Updating a CR to 'rejected' adds committed_at time to the CR.
                update_comment = Comment(
                    type='update', 
                    content=f"msg|Status changed to 'rejected'",
                    submitted_by=client_session.user_credentials.internal_id
                    )
                change_update.comments = [update_comment]
                change_update.reviewed_by = client_session.user_credentials.internal_id
                change_update.committed_at = datetime.now(UTC)

                
        return await self.validation_queue_repo.update(update=change_update)
    
    async def update_data(
        self,
        client_session: SessionExtended, 
        change_request_id: int, 
        entity_data: dict
    ) -> ChangeRequestRead:
        """
        Updates the entity data of a Change Request the user submitted. 
        Updates on CRs where the validation_status == 'pending' will return to the pending tab for a fresh review

        :raises ValidationError: User attempts to update a Change Request not submitted by them
        """
        
        change_request_old: ChangeRequestRead = await self.validation_queue_repo.get_one(change_request_id=change_request_id)

        if change_request_old.submitted_by != client_session.user_credentials.internal_id:
            raise ValidationError(
                origin="ChangeRequestService.update_data",
                status_code=403,
                message="Insufficent credentials to modify this change request"
                )
        else:
            content_dict = {"old": change_request_old.entity_data, "new": entity_data}
            update_comment = Comment(
                type="update",
                content=f"msg|Change Request modified|data_type|entity_data|data|{json.dumps(content_dict)}",
                submitted_by=client_session.user_credentials.internal_id
            )

            update = ChangeRequestUpdate(
                id=change_request_id, 
                comments=[update_comment],
                entity_data=entity_data
                )
            
            results = await self.validation_queue_repo.update(update=update)

            # If a change request being updated has a validation_status == 'pending', it means at some point the CR was under review and should be put up for review again. 
            # we cannot check vote_type because some requests without a vote_type can still be posted to pending for an optional review.
            # self.update_status with status='pending' performs all tasks nessesary to restart a review.
            if change_request_old.validation_status == 'pending':
                results = await self.update_status(client_session=client_session, change_request_id=change_request_id, status='pending')
            
            return results
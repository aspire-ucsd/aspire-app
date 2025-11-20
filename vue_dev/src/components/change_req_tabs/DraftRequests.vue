<script setup>
import { ref, onBeforeMount, onMounted, computed } from 'vue';
import axios from 'axios';
import CardBase from './request_cards/CardBase.vue'
import PageNav from '../utility_comps/PageNav.vue'

const contextData = window.contextData
const changeRequests = ref([])
const changeRequestSlice = ref([])
const currentIndex = ref(null)

const submitModalConfig = ref({is_open: false, vote_type: null, id: null, index: null})
const updateParams = ref({id: null, entity_data_copy: {}})

const timezone = ref('')

onMounted(() => {
    timezone.value = Intl.DateTimeFormat().resolvedOptions().timeZone
});

onBeforeMount(async () => {
    axios.get(`${contextData.tool_domain}/domain/changes/drafts`).then((response) => {
        changeRequests.value = response.data
        changeRequestSlice.value = response.data.slice(currentIndex.value, currentIndex.value + 4)
        currentIndex.value = 0  // Forces page indicators to update after data comes in
    })
})



const updateIndex = (increment) => {
    if ((currentIndex.value + increment) >= 0 && (currentIndex.value + increment) <= changeRequests.value.length) {
        currentIndex.value += increment
        changeRequestSlice.value = changeRequests.value.slice(currentIndex.value, currentIndex.value + 4)
    }
}

const pageSelect = (number, increment) => {
    if (typeof(number) === 'number') {
        const new_index = (number * increment) - increment
        currentIndex.value = new_index
        updateIndex(0)
    }
}

const nextCloseTime = computed(() => {
    const systemTimeZone = 'America/Los_Angeles'

    const now = new Date()

    // Convert current time to the system timezone
    const systemTime = new Date(
    now.toLocaleString('en-US', { timeZone: systemTimeZone })
    )

    // Generate potential closing times for today and tomorrow in the system timezone
    const todayNoonRaw = new Date(systemTime)
    todayNoonRaw.setHours(12, 0, 0, 0)
    const todayNoon = new Date(todayNoonRaw.toLocaleString('en-US', { timeZone: systemTimeZone }))

    const todayFivePMRaw = new Date(systemTime)
    todayFivePMRaw.setHours(17, 0, 0, 0)
    const todayFivePM = new Date(todayFivePMRaw.toLocaleString('en-US', { timeZone: systemTimeZone }))

    const tomorrowNoon = new Date(todayNoon)
    tomorrowNoon.setDate(todayNoon.getDate() + 1)

    // List of potential times in the system timezone
    const potentialClosingTimes = [todayNoon, todayFivePM, tomorrowNoon]

    // Find the next valid closing time
    const twoHoursLater = new Date(systemTime)
    twoHoursLater.setHours(systemTime.getHours() + 2)

    const nextValidClosingTime = potentialClosingTimes.find(
        (time) => time > systemTime && time > twoHoursLater
    )

    // Convert the next closing time to the user's timezone
    const userClosingTime = nextValidClosingTime.toLocaleString('en-US', { timeZone: timezone.value })

    return userClosingTime
})


const submitRequestStart = (changeRequest, index) => {
    // If no modification_type is present, this means the entity associated with the CR already exists and 
    // the SME only needs to review the entity_data prior to running the post_approval_procedure. No confirmation modal required
    // Most often occurs when identifying concepts with the LLM.
    if (!changeRequest.modification_type) {
        submitModalConfig.value = {is_open: false, vote_required: changeRequest.vote_type, id: changeRequest.id, index: index}
        submitRequest('approved')
    } else {
        submitModalConfig.value = {is_open: true, vote_required: changeRequest.vote_type, id: changeRequest.id, index: index}
    }
}

const discardRequestStart = (changeRequest, index) => {
    axios.delete(`${contextData.tool_domain}/domain/changes/draft?change_request_id=${changeRequest.id}`).then(() => {
        changeRequests.value.splice(index + currentIndex.value, 1)
        updateIndex(0)
        submitModalConfig.value = {is_open: false, vote_type: null, id: null, index: null}
    })
}

const submitRequest = (status) => {
    axios.put(`${contextData.tool_domain}/domain/changes/status?change_request_id=${submitModalConfig.value.id}&status=${status}`).then(() => {
        changeRequests.value.splice(submitModalConfig.value.index + currentIndex.value, 1)
        updateIndex(0)
        submitModalConfig.value = {is_open: false, vote_type: null, id: null, index: null}
    })
}

const confirmUpdate = (changeRequest) => {
    axios.put(`${contextData.tool_domain}/domain/changes?change_request_id=${changeRequest.id}`, changeRequest.entity_data).then(() => {
        updateParams.value.id = null
        updateParams.value.update_data = {}

    })
}

</script>

<template>
    <div class="draft-main">
        <div class="draft-interface">
            <div class="search-filter-btn">
                <img class="search-filter-icon" src="/aspire/static/assets/icon-search-white.png" />
                <p>Filter & Sort</p>
            </div>
            <PageNav 
                :page-increment="4" 
                v-model:current-page="currentIndex" 
                v-model:page-total="changeRequests.length"
                @page-up="updateIndex" 
                @page-down="updateIndex" 
                @page-select="pageSelect"
                />
            <div class="grid-view-btn">
                <img src="/aspire/static/assets/icon-grid-view-white.png" aria-label="Grid View" title="Grid View" />
            </div>
        </div>
        <div class="pending-requests">
            <CardBase 
                v-for="[index, changeRequest] of changeRequestSlice.entries()" 
                :key="changeRequest.id"
                :change-request="changeRequest" 
                :index="index"
                :timezone="timezone"
                :update-params="updateParams"
            >
                <div 
                    class="action-box"
                    v-if="updateParams.id !== changeRequest.id"
                >
                    <button 
                        @click="() => submitRequestStart(changeRequest, index)"
                        class="approve-button"
                    >
                        Submit
                    </button>
                    <button
                        v-if="changeRequest.modification_type !== 'delete' && changeRequest.entity_type !== 'concept_to_concept'"
                        @click="
                        () => {
                            updateParams.id = changeRequest.id
                            updateParams.entity_data_copy = {...changeRequest.entity_data}
                            }
                        "
                        class="update-request-btn"
                    >
                        Modify
                    </button>
                    <button 
                    @click="() => discardRequestStart(changeRequest, index)"
                    class="reject-button"
                    >
                        Discard
                    </button>
                </div>
                <div 
                    class="action-box"
                    v-else
                >
                    <button 
                        @click="() => confirmUpdate(changeRequest)"
                        class="approve-button"
                    >
                        Confirm
                    </button>
                    <button 
                    @click="
                        () => {
                            changeRequest.entity_data = updateParams.entity_data_copy
                            updateParams.id = null
                            updateParams.update_data = {}
                        }
                    "
                    class="reject-button"
                    >
                        Discard
                    </button>
                </div>
            </CardBase>
        </div>
    </div>

    <div 
        v-if="submitModalConfig.is_open && !submitModalConfig.vote_required"
        class="submit-modal"
    >
        <div
            class="submit-options"
        >
            <img 
                src="/aspire/static/assets/icon-close-blue.png"
                @click="() => submitModalConfig = {is_open: false, vote_type: null, id: null, index: null}"
            />
            <h3>Would you like this change to be reviewed by other Subject Matter Experts?</h3>
            <hr />
            <p>
                This request has been identified as having a negligible impact on the domains of other courses. 
                Requests of this type are subject to no review, however one may be posted if desired. 
                If you elect to place this request under review, relevant Subject Matter Experts will receive a period of time to review and vote on the change.
                <br />
                <br />
                This period will end after: <u>{{ nextCloseTime }}</u>
                <br />
                <br />
                You may end this review <strong><u>AT ANY TIME</u></strong>.
                <br />
                <br />
                At the conclusion of the review period, the Change Request may receive final confirmation or rejection, irrespective of the vote tally.
                If no other experts are found to be relevant to the change, no review will be offered and the Change Request will immediately be promoted to the 'domain'. 
                <br />
                <br />
                Final confirmation or rejection of Change Requests is accessible from your 'closed' tab.
                <br />
                <br />
                Select <strong>No</strong> to immediately promote this change to the 'Domain Model'.
                <br />
                <br />
                Select <strong>Yes</strong> to open a review.
            </p>
            <hr />
            <div class="action-box">
                <button 
                    @click="() => submitRequest('pending')"
                    class="approve-button"
                >
                    Yes
                </button>
                <button 
                @click="() => submitRequest('approved')"
                class="reject-button"
                >
                    No
                </button>
            </div>
            
        </div>
    </div>

    <div 
        v-if="submitModalConfig.is_open && submitModalConfig.vote_required === 'veto'"
        class="submit-modal"
    >
        <div
            class="submit-options"
        >
            <img 
                src="/aspire/static/assets/icon-close-blue.png"
                @click="() => submitModalConfig = {is_open: false, vote_type: null, id: null, index: null}"
            />
            <h3>Submit Request for Veto Review</h3>
            <hr />
            <p>
                This request has been identified as having a significant impact on the domains of other courses. 
                Requests of this type are subject to a veto-style vote where impacted Subject Matter Experts will receive a period of time to review or veto the change.
                <br />
                <br />
                This period will end after: <u>{{ nextCloseTime }}</u>
                <br />
                <br />
                At the conclusion of the review period, if no veto is cast, the Change Request may receive final confirmation or rejection.
                If no other experts are found to be impacted, no review will be offered and the Change Request may immediately receive final confirmation or rejection. 
                <br />
                <br />
                Final confirmation or rejection of Change Requests is accessible from your 'closed' tab.
                <br />
                <br />
                Select <strong>Confirm</strong> to open the review.

            </p>
            <hr />
            <div class="action-box">
                <button 
                    @click="() => submitRequest('pending')"
                    class="approve-button"
                >
                    Confirm
                </button>
            </div>
            
        </div>
        
    </div>

    <div 
        v-if="submitModalConfig.is_open && submitModalConfig.vote_required === 'simple_majority'"
        class="submit-modal"
    >
        <div
            class="submit-options"
        >
            <img 
                src="/aspire/static/assets/icon-close-blue.png"
                @click="() => submitModalConfig = {is_open: false, vote_type: null, id: null, index: null}"
            />
            <h3>Submit Request for Simple Majority Review</h3>
            <hr />
            <p>
                This request has been identified as having a moderate impact on the domains of other courses. 
                Requests of this type are subject to a simple majority vote where impacted Subject Matter Experts will receive a period of time to review and vote on the change.
                <br />
                <br />
                This period will end after: <u>{{ nextCloseTime }}</u>
                <br />
                <br />
                At the conclusion of the review period, the final vote tally determines if the request may receive final confirmation or rejection, ties default to a rejection.
                If no other experts are found to be impacted, no review will be offered and the Change Request may immediately receive final confirmation or rejection. 
                <br />
                <br />
                Final confirmation or rejection actions are accessible from your 'closed' tab.
                <br />
                <br />
                Select <strong>Confirm</strong> to open the review.
            </p>
            <hr />
            <div class="action-box">
                <button 
                    @click="() => submitRequest('pending')"
                    class="approve-button"
                >
                    Confirm
                </button>
            </div>
            
        </div>
    </div>

</template>

<style scoped>
.draft-main {
    width: 100%;
    height: 94%;
    display: flex;
    flex-direction: column;
    box-shadow: 0px 0px 1px var(--border-shadow) inset;
    padding: 1rem;
}

.draft-interface {
    height: 6%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.search-filter-btn {
    position: absolute;
    left: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    background-color: var(--core-primary);
    color: var(--text-color-alt);
    width: 12%;
    height: 75%;
    border-top-right-radius: 1rem;
    border-bottom-left-radius: 1rem;
}

.search-filter-icon {
    aspect-ratio: 1/1;
    height: 80%;
}

.grid-view-btn {
    aspect-ratio: 1/1;
    height: 100%;
    position: absolute;
    right: 0;
    background-color: var(--core-primary);
    border-radius: 0.5rem;
}

.grid-view-btn>img {
    aspect-ratio: 1/1;
    height: 100%;
}

.pending-requests {
    display: flex;
    flex-direction: row;
    height: 94%;
    width: 100%;
    position: relative;
}

.action-box{
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-evenly;
}
.action-box > button {
    padding: 0.5rem;
    width: 30%;
    height: 2rem;
    border-radius: 1rem;
    border: 0px;
    color: white;
    font-weight: bold;
}

.approve-button {
    background-color: var(--success-green);
}

.approve-button:hover {
    background-color: var(--success-green-highlight);
}

.approve-button:active {
    background-color: var(--success-green-muted);
}

.update-request-btn {
    background-color: var(--update-indigo);
}

.update-request-btn:hover {
    background-color: var(--update-indigo-highlight);
}
.update-request-btn:active {
    background-color: var(--update-indigo-muted);
}
.update-proposal-btn {
    background-color: var(--update-indigo);
}
.update-proposal-btn:hover {
    background-color: var(--update-indigo-highlight);
}
.update-proposal-btn:active {
    background-color: var(--update-indigo-muted);
}
.reject-button {
    background-color: var(--danger-red);
}

.reject-button:hover {
    background-color: var(--danger-red-highlight);
}

.reject-button:active {
    background-color: var(--danger-red-muted);
}

.submit-modal {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 100%;
    z-index: 100;
    background-color: rgba(128, 128, 128, 0.347);
    display: flex;
    align-items: center;
    justify-content: center;
}

.submit-options{
    position: relative;
    max-width: 75%;
    background-color: var(--bg-color);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    row-gap: 1rem;

}
.submit-options > h3 {
    margin-right: 1.5rem;
}

.submit-options > hr {
    width: 100%;
}

.submit-options > img {
    position: absolute;
    top: 0;
    right: 0;
    aspect-ratio: 1/1;
    width: 2rem;
}
</style>
<script setup>
/* eslint-disable */
import { ref, defineProps, computed, reactive, defineEmits, defineModel } from 'vue';
import CreateDeleteConceptRequest from "./CreateDeleteConceptRequest.vue"
import ConceptJunctionRequest from './ConceptJunctionRequest.vue';
import CommentContent from './CommentContent.vue';
import axios from 'axios';

const props = defineProps(['changeRequest', 'updateParams', 'index', 'timezone', 'config'])

const isExpanded = ref(false)
const changeRequest = reactive(props.changeRequest)
const showComments = ref(false)

const cardType = computed(() => {
    const mapping = {
        concept: {
            create: {
                'component': CreateDeleteConceptRequest,
                'banner_color': 'var(--success-green)',
                'cardTitle': 'Create New Concept'

            },
            update: {
                'component': 'ConceptCard',
                'banner_color': 'var(--update-indigo)',
                'cardTitle': 'Update Concept'

            },
            delete: {
                'component': CreateDeleteConceptRequest,
                'banner_color': 'var(--danger-red)',
                'cardTitle': 'Delete Concept'

            },
            null: {
                'component': CreateDeleteConceptRequest,
                'banner_color': 'var(--success-green-muted)',
                'cardTitle': 'Review Existing Concept for Addition in Course'
            }
        },
        concept_to_concept: {
            create: {
                'component': ConceptJunctionRequest,
                'banner_color': 'var(--success-green)',
                'cardTitle': 'Create New Concept to Concept Junction'

            },
            delete: {
                'component': ConceptJunctionRequest,
                'banner_color': 'var(--danger-red)',
                'cardTitle': 'Delete Existing Concept to Concept Junction'

            }
        },
        question: {
            create: "QuestionCard",
            update: "QuestionCard",
            delete: "QuestionCard",
        }
    }
    return mapping[changeRequest.entity_type]?.[changeRequest.modification_type] || 'DefaultCard'
})



const progressBarStyle = computed(() => {
    const approved = changeRequest.votes.filter(vote => vote === 'approved').length
    const rejected = Math.abs(approved - changeRequest.votes.length)
    const proportion = (changeRequest.votes.filter(vote => vote === 'approved').length / changeRequest.votes.length) * 100
    return {
        proportion: proportion,
        approved: approved,
        rejected: rejected,
        style: {
            background: `linear-gradient(to right, var(--success-green) ${proportion - 10}%, var(--danger-red) ${proportion + 10}%, var(--danger-red) 100%)`,
        }
    };
})



const convertDatetimeTZ = (utcDatetime, timezone) => {

    const options = { 
        timeZone: timezone, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit',
        year: 'numeric',
        month: 'numeric',
        day: 'numeric', 
    };
    const utcDate = new Date(utcDatetime).toLocaleString('en-US', options);
    return new Date(utcDate)
    
};

const calculateDelta = (utcDatetime, timezone) => {
    const now = new Date()
    const targetTime = convertDatetimeTZ(utcDatetime, timezone)
    // console.log(`Timezone: ${timezone}\nUTC Date: ${utcDatetime}\nNow: ${now}\nTarget Time: ${targetTime}`)
    const deltaMs = Math.abs(targetTime - now)

    const days = Math.floor(deltaMs / (1000 * 60 * 60 * 24))
    const hours = Math.floor((deltaMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
    const minutes = Math.floor((deltaMs % (1000 * 60 * 60)) / (1000 * 60))

    return { days, hours, minutes};
};

const cardAge = calculateDelta(changeRequest.submitted_at, props.timezone)
const timeRemaining = changeRequest.closes_at ? calculateDelta(changeRequest.closes_at, props.timezone) : null

const contextData = window.contextData

const commentValue = ref('')

const commentStyle = (comment) => {
    if (comment.type === 'update') {
        return 'comment-base comment-update'
    }
    else if (comment.type === 'proposal') {
        return 'comment-base comment-proposal'
    }
    else if (comment.type === 'approve_vote') {
        return 'comment-base comment-vote-approve'
    }    
    else if (comment.type === 'reject_vote') {
        return 'comment-base comment-vote-reject'
    }
    else if (comment.submitted_by === Number(contextData.aspire_id)) {
        return 'comment-base comment-owner'
    } else {
        return 'comment-base comment-other'
    }
}

const addComment = () => {
    changeRequest.comments.push({type: 'text', content: commentValue.value, submitted_by: Number(contextData.aspire_id), submitted_at: Date.now()})

    const data = {type: 'text', content: commentValue.value}
    axios.put(`${contextData.tool_domain}/domain/changes/comment?request_id=${changeRequest.id}`, data).then(() => {
        commentValue.value = ''
    })
}


</script>

<template>
    <div :class="isExpanded ? 'card-base card-expanded' : 'card-base card-collapsed'">
        <div class="card-info-tabs">
            <div class="card-top-tab card-age">
                {{`Created ${cardAge.days}d - ${cardAge.hours}h Ago`}}
            </div>
            <div 
                v-if="changeRequest.is_from_llm"
                class="card-top-tab card-from-llm"
            >
                LLM
            </div>
            <div 
                v-if="changeRequest.submitted_by === Number(contextData.aspire_id)"
                class="card-top-tab card-is-mine"
            >
                Owner
            </div>
        </div>
        <div class="card-body">
            <div class="card-banner" :style="{backgroundColor: cardType.banner_color || 'var(--success-green-muted)'}">
                <div 
                    v-if="changeRequest.closes_at"
                    class="vote-time"
                >
                    <h4>{{props.config?.time_remaining_tense || 'Closes:'}}</h4>
                    <p>{{ `${timeRemaining.days}d - ${timeRemaining.hours}h - ${timeRemaining.minutes}m` }}</p>

                </div>
                <hr v-if="timeRemaining?.hours"/>
                <div>
                    <!-- <h3>{{ `${changeRequest?.modification_type || 'Review Existing'} ${changeRequest?.entity_type || 'change'}` }}</h3> -->
                    <h3>{{ cardType.cardTitle }}</h3>
                </div>
                <img 
                    :src="isExpanded ? '/aspire/static/assets/icon-collapse-content-white.png' : '/aspire/static/assets/icon-expand-content-white.png'"
                    class="card-expand-btn"
                    :aria-label="isExpanded ? 'Collapsed View': 'Expanded View'"
                    :title="isExpanded ? 'Collapsed View': 'Expanded View'"
                    @click="() => isExpanded = !isExpanded"
                />
            </div>
            <div class="card-info" :data-state="showComments">
                <component 
                    :is="cardType.component" 
                    :is-expanded="isExpanded" 
                    v-model:change-request="changeRequest"
                    :update-params="updateParams"
                    />
            </div>
            <hr class="card-hr"/>
            <div class="card-comments" :data-state="showComments">
                <div class="comment-interface">
                    <p><strong>Comments: </strong>{{ changeRequest.comments.length }}</p>
                    <img 
                        src="/aspire/static/assets/icon-chevron-left-blue.png"
                        @click="() => showComments = !showComments"
                    />
                </div>
                <div 
                    class="comment-section"
                >
                    <div
                        v-for="comment of changeRequest.comments"
                        :class="commentStyle(comment)"
                    >
                        <p class="comment-age">{{ `${calculateDelta(comment.submitted_at, props.timezone).days}d - ${calculateDelta(comment.submitted_at, props.timezone).hours}h - ${calculateDelta(comment.submitted_at, props.timezone).minutes}m` }}</p>
                        <CommentContent
                            :comment="comment"
                        
                        />
                    </div>
                    <div class="comment-typing-area">
                        <textarea
                            v-model="commentValue"
                            class="comment-textarea"
                            placeholder="Type Comment here..."
                        ></textarea>
                        <img 
                            src="/aspire/static/assets/icon-comment-blue.png"
                            class="add-comment-btn"
                            @click="addComment"
                            />
                    </div>

                </div>
            </div>
            <hr class="card-hr"/>
            <div class="card-actions">
                <slot >
                    
                </slot>
                <div 
                    class="vote-tally" 
                    :style="progressBarStyle.style"
                    v-if="progressBarStyle.proportion >= 0"
                >
                    <p><strong>Approved:</strong> {{ Math.round(progressBarStyle.approved) }}</p>
                    <p><strong>Rejected:</strong> {{ Math.round(progressBarStyle.rejected) }}</p>
                </div>
            </div>
        </div>
    </div>
    <div v-if="isExpanded" class="card-base">

    </div>
</template>

<style scoped>
.card-base {
    margin: 1rem;
    width: calc((100% / 4) - 2rem);
    height: calc(100% - 2rem);
    transition: width 0.3s ease;
    z-index: 1;
}

.card-expanded {
    position: absolute;
    left: 0;
    right: 0;
    height: calc(100% - 2rem); /* Expanded height */
    z-index: 10; /* Bring the expanded card to the front */
    width: calc(100% - 2rem); /* Optional: slightly zoom */
    transition: width 0.3s ease;
}
.card-body {
    background-color: var(--bg-accent);
    height: 97%;
    border-radius: 10px;
    box-shadow: 0px 0.5px 4px 0px rgb(97, 97, 97);
}
.card-info-tabs{
    height: 3%;
    display: flex;
    flex-direction: row;
    column-gap: 1rem;
    padding-left: 10px;
    padding-right: 10px;
    background-color: var(--bg-color);
    
}
.card-top-tab {
    padding: 0.25rem;
    border-top-right-radius: 12px;
    border-top-left-radius: 4px;
    color: var(--bg-color);
    font-size: small;
    box-shadow: 0px 1px 4px 0px rgb(97, 97, 97);

}
.card-age {
    background-color: var(--bg-contrast);
}

.card-from-llm {
    background-color: var(--llm-green);
}

.card-is-mine {
    background-color: var(--core-secondary);
}
.card-banner{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    width: 100%;
    height: 10%;
    border-top-right-radius: 10px;
    border-top-left-radius: 10px;
    color: var(--bg-color)

}
.card-banner > hr {
    height: 95%;
    width: 2px;
}
.vote-time {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.vote-time > h4 {
    font-size:medium;
}
.vote-time > p {
    font-size: small;
}

.card-expand-btn{
    aspect-ratio: 1/1;
    height: 50%;
    transform: rotate(0deg);
    transition: transform 0.5s ease-in-out;
}
.card-expand-btn:hover {
    transform: rotate(45deg);
}
.card-expand-btn:active {
    filter: drop-shadow(0px 0px 4px var(--text-muted));
}

.card-info {
    overflow: hidden;
    height: 74%;
}
@keyframes shrink_and_hide {
    from {
        height: 74%;
        visibility: visible;
    }
    to {
        height: 0%;
        visibility: hidden;
    }
}
@keyframes expand_and_show {
    from {
        height: 0%;
        visibility: hidden;
    }
    to {
        height: 74%;
        visibility: visible;
    }
}
.card-info[data-state=false] {
    height: 74%;
    visibility: visible;
    animation: expand_and_show 0.3s ease-in-out;
}
.card-info[data-state=true] {
    height: 0%;
    visibility: hidden;
    animation: shrink_and_hide 0.3s ease-in-out;
}

.card-comments {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    transition: height 0.3s ease-in-out;
    overflow: hidden;
}
.card-comments[data-state=false] {
    height: 2.5rem;
}
.card-comments[data-state=true] {
    height: 80%;
}
.comment-interface {
    height: 2.5rem;
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    text-align: center;
    justify-content: space-between;
    padding-left: 0.5rem;
    transition: height 0.1s ease-in-out;
}

.comment-interface > img {
    aspect-ratio: 1/1;
    height: 100%;
    transition: transform 0.3s ease-in-out;
}
.card-comments[data-state=false] > .comment-interface > img {
    transform: rotate(90deg);
}

.card-comments[data-state=true] > .comment-interface > img {
    transform: rotate(-90deg);
}

.comment-section {
    height: calc(100% - 2.5rem);
    width:100%;
    background-color: white;
    display: flex;
    flex-direction: column;
    overflow-y: scroll;
}
.comment-base {
    margin: 0.5rem;
    display: flex;
    flex-direction: column;
    width: fit-content;
    padding: 0.5rem;
    color: var(--text-color-alt);

}

.comment-owner {
    background-color: var(--core-secondary);
    margin-left: 1rem;
    border-bottom-right-radius: 1rem;
    border-top-left-radius: 1rem;
    align-items:flex-end;
    align-self: flex-end;

}

.comment-other {
    background-color: var(--bg-contrast);
    margin-right: 1rem;
    align-items:flex-start;
    align-self: flex-start;
    border-bottom-left-radius: 1rem;
    border-top-right-radius: 1rem;

}

.comment-vote-approve {
    background-color: var(--success-green);
    margin-left: 1rem;
    border-bottom-right-radius: 1rem;
    border-top-left-radius: 1rem;
    align-items:flex-end;
    align-self: flex-end;
}

.comment-vote-reject {
    background-color: var(--danger-red);
    margin-right: 1rem;
    align-items:flex-start;
    align-self: flex-start;
    border-bottom-left-radius: 1rem;
    border-top-right-radius: 1rem;

}

.comment-update {
    background-color: var(--update-indigo);
    align-items:center;
    align-self: center;
}
.comment-proposal {
    background-color: var(--update-indigo-muted);
    align-items:center;
    align-self: center;
}
.comment-typing-area {
    position: relative;
}

.add-comment-btn {
    position: absolute;
    top: 0;
    right: 0;
    height: 40%;
    aspect-ratio: 1/1;
    padding: 0.5rem;
}

.add-comment-btn:hover {
    filter: drop-shadow(0px 0px 1px var(--core-primary));
}
.comment-textarea {
    width: 100%;
    max-width: 100%;
    min-height: 6rem;
    box-sizing: border-box;
    resize: vertical;
    padding: 8px;
    font-size: 14px;
}
.comment-age {
    font-size: small;
}
.card-hr {
    border: 1px solid var(--bg-color);
}
.card-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-evenly;
    height: 10%;
}

.vote-tally {
    width: 90%;
    height: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    font-size: small;
    color: var(--bg-color);
    border-radius: 0.85rem;
}
</style>
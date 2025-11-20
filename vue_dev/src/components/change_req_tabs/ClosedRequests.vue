<script setup>
import { ref, onBeforeMount, onMounted } from 'vue';
import axios from 'axios';
import CardBase from './request_cards/CardBase.vue'
import PageNav from '../utility_comps/PageNav.vue'

const contextData = window.contextData
const changeRequests = ref([])
const changeRequestSlice = ref([])
const currentIndex = ref(null)
const updateParams = ref({id: null, entity_data_copy: {}})

const timezone = ref('')

const cardConfig = {
    time_remaining_tense: "Closed:"
}

const canApprove = (changeRequest) => {
    const is_allowed = 
        (
        changeRequest.vote_type 
        && 
        (changeRequest.votes.filter(vote => vote === 'approved').length / changeRequest.votes.length) > 0.5
        ) 
        || 
        !changeRequest.vote_type 
        || 
        changeRequest.votes.length === 0
    return is_allowed
}

onMounted(() => {
    timezone.value = Intl.DateTimeFormat().resolvedOptions().timeZone
});

onBeforeMount(async () => {
    axios.get(`${contextData.tool_domain}/domain/changes/closed`).then((response) => {
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

const confirmUpdate = (changeRequest, index) => {
    axios.put(`${contextData.tool_domain}/domain/changes?change_request_id=${changeRequest.id}`, changeRequest.entity_data).then(() => {
        updateParams.value.id = null
        updateParams.value.update_data = {}
        changeRequests.value.splice(index + currentIndex.value, 1)
        updateIndex(0)
    })
}

const submitRequest = (index, changeRequestId, status) => {
    axios.put(`${contextData.tool_domain}/domain/changes/status?change_request_id=${changeRequestId}&status=${status}`).then(() => {
        changeRequests.value.splice(index + currentIndex.value, 1)
        updateIndex(0)
    })
}

</script>

<template>
    <div class="pending-main">
        <div class="pending-interface">
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
                :config="cardConfig"
            >
                <div 
                    class="action-box"
                    v-if="updateParams.id !== changeRequest.id"
                >
                    <button 
                        v-if="canApprove(changeRequest)"
                        @click="() => submitRequest(index, changeRequest.id, 'approved')"
                        class="approve-button"
                    >
                        Confirm
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
                        Update
                    </button>
                    <button 
                    @click="() => submitRequest(index, changeRequest.id, 'rejected')"
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
                        @click="() => confirmUpdate(changeRequest, index)"
                        class="approve-button"
                    >
                        Update
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
</template>

<style scoped>
.pending-main {
    width: 100%;
    height: 94%;
    display: flex;
    flex-direction: column;
    box-shadow: 0px 0px 1px var(--border-shadow) inset;
    padding: 1rem;
}

.pending-interface {
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
</style>
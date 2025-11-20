<script>
export default {
    name: 'ChangeRequests',
    view: 'student',
    friendly_name: "Domain Change Requests",
    icon: "/aspire/static/assets/icon-change-request-page.png",
    props: {
        msg: String
    }
}
</script>
<script setup>
import { ref } from "vue"
import PendingRequests from '../components/change_req_tabs/PendingRequests.vue'
import ClosedRequests from '../components/change_req_tabs/ClosedRequests.vue'
import DraftRequests from '../components/change_req_tabs/DraftRequests.vue'


const activeTab = ref('pending')
const tabs = {'pending': PendingRequests, 'closed': ClosedRequests, 'draft': DraftRequests, 'history': 'test'}
</script>

<template>
    <div class="validation-main">
        <div class="validation-tabs">
            <div 
                class="tab no-select roboto-bold" 
                :data-state="activeTab === 'pending'"
                @click="() => activeTab = 'pending'"
            >
                Pending
            </div>
            <div 
                class="tab no-select roboto-bold" 
                :data-state="activeTab === 'closed'"
                @click="() => activeTab = 'closed'"
                >
                Closed
            </div>
            <div 
                class="tab no-select roboto-bold" 
                :data-state="activeTab === 'draft'"
                @click="() => activeTab = 'draft'"
                >
                Drafts
            </div>
            <div 
                class="tab no-select roboto-bold" 
                :data-state="activeTab === 'history'"
                @click="() => activeTab = 'history'"
                >
                Change History
            </div>
        </div>
        <component :is="tabs[activeTab]"/>
    </div>
</template>

<style scoped>
.validation-main {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.validation-tabs {
    width: 100%;
    height: 6%;
    display: flex;
    flex-direction: row;
    justify-content: space-evenly;
    align-items:end;
    overflow: hidden;
}

.tab {
    width: 25%;
    height: 100%;
    padding: 0.5rem;
    background-color: var(--core-secondary);
    background-color: var(--core-primary);

    -webkit-clip-path: polygon(0 0, 85% 0, 100% 50%, 100% 100%, 100% 100%, 0 100%, 0 100%, 0 0);
    clip-path: polygon(0 0, 85% 0, 100% 50%, 100% 100%, 100% 100%, 0 100%, 0 100%, 0 0);
    border-top-right-radius: 55%;
    transform: translateY(20px);
    border-top-left-radius: 8px;
    color: var(--text-color-alt)
}

.tab:hover{
    transform: translateY(0);
}

.tab[data-state=true]{
    transform: translateY(0);
    background-color: var(--core-secondary);
}
</style>
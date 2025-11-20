<script setup>
import { reactive, ref, defineProps } from 'vue';

const props = defineProps(['tabs'])

const draggableContainer = ref()
const activeTab = ref(props.tabs[0]?.id)

const positions = reactive({
        clientX: undefined,
        clientY: undefined,
        movementX: 0,
        movementY: 0
    }
)

const dragMouseDown = (event) => {
    event.preventDefault()
    // get the mouse cursor position at startup:
    positions.clientX = event.clientX
    positions.clientY = event.clientY
    document.onmousemove = elementDrag
    document.onmouseup = closeDragElement
    }

const elementDrag = (event) => {
    event.preventDefault()
    positions.movementX = positions.clientX - event.clientX
    positions.movementY = positions.clientY - event.clientY
    positions.clientX = event.clientX
    positions.clientY = event.clientY

    draggableContainer.value.style.top = (draggableContainer.value.offsetTop - positions.movementY) + 'px'
    draggableContainer.value.style.left = (draggableContainer.value.offsetLeft - positions.movementX) + 'px'
    }

const closeDragElement = () => {
    document.onmouseup = null
    document.onmousemove = null
}

console.log(activeTab.value)

</script>

<template>
    <div ref="draggableContainer" id="draggable-settings-container">
        <div id="draggable-settings-header" @mousedown="dragMouseDown">
        <slot name="header"></slot>
        </div>
        <div class="settings-tabs">
            <div
                class="settings-tab-buttons"  
            >
                <span
                    class="tab-select no-select"
                    v-for="tab of props.tabs"
                    :data-state="activeTab === tab.id"
                    :key="tab.id"
                    @click="() => activeTab = tab.id "
                >
                    {{ tab.name }}
                </span>
            </div>
            <hr />
            <div
                v-for="tab of props.tabs"
                :key="tab + 'content'"
            >   
                <slot :name="tab.id" v-if="activeTab === tab.id"></slot>
            </div>
        </div>
    </div>
</template>


<style>
.settings-tabs {
    display: flex;
    flex-direction: column;
}

.settings-tab-buttons {
    display: flex;
    flex-direction: row;
    /* align-items: center; */
    justify-content: space-between;
    align-items:end;
    overflow: hidden;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-top: 0.5rem;
    background-color: var(--bg-color);
}
.tab-select {
    height: 100%;
    padding: 0.5rem;
    background-color: var(--core-secondary);
    background-color: var(--core-primary);

    -webkit-clip-path: polygon(0 0, 85% 0, 100% 50%, 100% 100%, 100% 100%, 0 100%, 0 100%, 0 0);
    clip-path: polygon(0 0, 85% 0, 100% 50%, 100% 100%, 100% 100%, 0 100%, 0 100%, 0 0);
    border-top-right-radius: 55%;
    transform: translateY(10px);
    border-top-left-radius: 8px;
    color: var(--text-color-alt)
}

.tab-select:hover{
    transform: translateY(0);
}

.tab-select[data-state=true]{
    transform: translateY(0);
    background-color: var(--core-secondary);
}

#draggable-settings-container {
position: absolute;
left: 25%;
top: 5%;
z-index: 999;
box-shadow: 0px 0px 3px -1px black;
border-radius: 1rem;
}
#draggable--settings-header {
z-index: 1000;
}
</style>
<script setup>
import { reactive, ref } from 'vue';

const draggableContainer = ref()

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

</script>

<template>
    <div ref="draggableContainer" id="draggable-container">
        <div id="draggable-header" @mousedown="dragMouseDown">
            <slot></slot>
        </div>
    </div>
</template>


<style>
#draggable-container {
position: absolute;
z-index: 999;
}
#draggable-header {
z-index: 1000;
}
</style>
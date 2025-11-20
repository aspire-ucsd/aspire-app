<script setup>
import { ref, defineProps, defineModel, nextTick } from 'vue'

const selectedValue = defineModel('selectedValue')
const props = defineProps(["optionMapping", "allow_multiple_selections"])

const menuRef = ref(null)
const contentWidth = ref(0);
const isOpen = ref(false)

function openToggle() {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
        nextTick(() => {
        contentWidth.value = menuRef.value.scrollWidth;
        });
    } else {
        contentWidth.value = 0;
    }
}

function selectOption(option) {
    if (props.allow_multiple_selections) {
        if (selectedValue.value.includes(option)) {
            selectedValue.value = selectedValue.value.filter(item => item !== option)
        } else {
            selectedValue.value.push(option)
        }
    } else {
        selectedValue.value = option
        isOpen.value = false
    }
}

</script>

<template>
    <div>
        <div class="dropdown-root" :data-state="isOpen" ref="menuRef">
            <span v-if="!props.allow_multiple_selections" class="dropdown-input">{{ props.optionMapping[selectedValue] }}</span>
            <span v-if="props.allow_multiple_selections" class="dropdown-input">{{ selectedValue }}</span>


            <img class="dropdown-icon" src="/aspire/static/assets/icon-chevron.png" @click="openToggle"/>
        </div>
        <div 
            class="item-box" 
            v-if="isOpen && !props.allow_multiple_selections"
            :style="{'width': isOpen ? `${contentWidth}px` : '0'}"
        >
            <span
                v-for="[id, value] of Object.entries(props.optionMapping)"
                :value="id"
                :key="id"
                class="dropdown-item"
                :data-state="selectedValue === id"
                @click="selectOption(id)"
            >
                {{ value }}
            </span>
        </div>
        <div 
            class="item-box" 
            v-if="isOpen && props.allow_multiple_selections"
            :style="{'width': isOpen ? `${contentWidth}px` : '0'}"
        >
            <span
                v-for="[id, value] of Object.entries(props.optionMapping)"
                :value="id"
                :key="id"
                class="dropdown-item"
                :data-state="selectedValue.includes(id)"
                @click="selectOption(id)"
            >
                {{ value }}
            </span>
        </div>
    </div>
</template>

<style scoped>
.item-box {
    width: 97%;
    display: flex;
    position: absolute;
    z-index: 999;
    flex-direction: column;
    max-height: 10rem;
    scrollbar-color: var(--accent-primary) var(--bg-color);
    scrollbar-width: thin;
    overflow-y: auto;
    overflow-x: hidden;
    background-color: var(--bg-color);
}
.dropdown-item {
    width: 100%;
    font-size: .75rem;
    font-weight: normal;
    padding: .25rem;
    border: 1px solid black;
}

.dropdown-item[data-state=true] {
background-color: greenyellow;
}

.dropdown-root {
    position: relative;
    border: 1px solid black;
    align-items: center;
    border-radius: 4px;
    width: 100%;
    height: 1.5rem;
    padding: 1px;
    display: flex;
    background-color: var(--bg-color);
}
.dropdown-input {
    border: none;
    background: none;
    width: calc(100% - 1rem);
}
.dropdown-input:focus {
    outline: none;
}

.dropdown-icon {
    height: 1.5rem;
}

.dropdown-root[data-state=true] > .dropdown-icon {
    transform: rotate(180deg);
    transition: 300ms linear;
}
.dropdown-root[data-state=false] > .dropdown-icon {
    transform: rotate(0deg);
    transition: 300ms linear;
}
</style>
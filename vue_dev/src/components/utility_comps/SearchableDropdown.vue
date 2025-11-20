<script setup>
import { ref, defineProps, defineModel } from 'vue'

const selectedValue = defineModel('selectedValue')
const props = defineProps(["items", "allow_multiple_selections"])


const searchTerm = ref('')
const isOpen = ref(false)

function validItems() {
    const items = Object.values(props.items).filter(item => item.name.toLowerCase().includes(searchTerm.value.toLowerCase()))
    return items
}

function openToggle() {
    if (searchTerm.value.length > 0) {
        isOpen.value = false
        searchTerm.value = ''
    } else {
        isOpen.value = !isOpen.value
    }
}

function selectItem(option) {
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
    <div class="search-root" :data-state="searchTerm.length > 0 || isOpen">
        <input class="search-input" type="text" :placeholder="selectedValue ? selectedValue : 'Search'" v-model="searchTerm"/>
        <img class="search-icon" src="/aspire/static/assets/icon-chevron.png" @click="openToggle"/>
    </div>
    <div class="item-box" v-if="searchTerm.length > 0 &&props.allow_multiple_selections || isOpen && props.allow_multiple_selections">
        <span
            v-for="(item, index) in validItems()"
            :value="item.id"
            :key="index"
            class="search-item"
            :data-state="selectedValue.includes(item.id)"
            @click="selectItem(item.id)"
        >
            {{ item.name }}
        </span>
    </div>
    <div class="item-box" v-if="searchTerm.length > 0 && !props.allow_multiple_selections || isOpen && !props.allow_multiple_selections">

        <span
            v-for="(item, index) in validItems()"
            :value="item.id"
            :key="index"
            class="search-item"
            :data-state="selectedValue == item.id"
            @click="selectItem(item.id)"
        >
            {{ item.name }}
        </span>
    </div>
</template>

<style scoped>
.item-box {
    width: calc(100%);
    display: flex;
    flex-direction: column;
    max-height: 20rem;
    scrollbar-color: var(--accent-primary) var(--bg-color);
    scrollbar-width: thin;
    overflow-y: scroll;
    overflow-x: hidden;
    padding-left: 1px;
    background-color: var(--bg-color);
}
.search-item {
    font-size: .75rem;
    font-weight: normal;
    padding: .25rem;
    border: 1px solid black;
}

.search-item[data-state=true] {
background-color: greenyellow;
}

.search-root {
    border: 1px solid black;
    border-radius: 4px;
    width: 100%;
    /* height: 1rem; */
    padding: 1px;
    display: flex;
    background-color: var(--bg-color);
}
.search-input {
    border: none;
    background: none;
    width: calc(100% - 1rem);
}
.search-input:focus {
    outline: none;
}

.search-icon {
    height: 1.5rem;
}

.search-root[data-state=true] > .search-icon {
    transform: rotate(180deg);
    transition: 300ms linear;
}
.search-root[data-state=false] > .search-icon {
    transform: rotate(0deg);
    transition: 300ms linear;
}
</style>
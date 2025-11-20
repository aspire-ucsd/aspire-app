<script setup>
import {onBeforeMount, ref} from "vue"
const subject_list = ref()

onBeforeMount(() => {
    //add api call for subject list
    subject_list.value = ["computer science", "physics"]
})

const searchTerm = ref('')

const isOpen = ref(false)

function validItem() {
    const items = Object.values(subject_list.value).filter(item => item.name.toLowerCase().includes(searchTerm.value.toLowerCase()))
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

function selectItem(item) {
    console.log(item)
}
</script>

<template>
    <div class="reg-start-root">
        <div class="search-root" :data-state="searchTerm.length > 0 || isOpen">
            <input class="search-input" type="text" placeholder="Search" v-model="searchTerm"/>
            <img class="search-icon" src="/static/assets/icon-chevron.png" @click="openToggle"/>
        </div>
        <div class="item-box" v-if="searchTerm.length > 0 || isOpen">
            <span
                v-for="item of validItem()"
                :value="item"
                :key="item"
                class="search-item"
                :data-state="true"
                @click="selectItem(item)"
            >
                {{ item }}
            </span>
        </div>

    </div>
</template>


<style scoped>
.reg-start-root {
    position: relative;
    height: 100%;
}
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
    background-color: var(--core-secondary);
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
<script setup>
/* eslint-disable */
import { ref, defineProps, defineEmits, defineModel, watch } from 'vue';

const props = defineProps(['pageIncrement'])
const emit = defineEmits(['pageUp', 'pageDown', 'pageSelect'])

const currentPage = defineModel('currentPage')
const pageTotal = defineModel('pageTotal')

const getPageIndicators = () => {
    if (pageTotal.value > 0) {
        const lastPage = Math.ceil(pageTotal.value / props.pageIncrement)
        const currentPageAdj = (currentPage.value / props.pageIncrement) + 1
        let results = [1]

        let currentPageGroup = [currentPageAdj - 2, currentPageAdj - 1, currentPageAdj, currentPageAdj + 1, currentPageAdj + 2].filter(val => val > 1 && val < lastPage)

        if (currentPageGroup[0] && (currentPageGroup[0] - 1) !== 1) {
            results.push("...")
        }

        results = results.concat(currentPageGroup)

        if (currentPageGroup[0] && (currentPageGroup.at(-1) + 1) !== lastPage) {
            results.push("...")
        }
        if (!results.includes(lastPage)) {
            results.push(lastPage)
        }

        return results
    }
}

const pageIndicators = ref(getPageIndicators())

watch(currentPage, () => {
    pageIndicators.value = getPageIndicators()
})

watch(pageTotal, () => {
    pageIndicators.value = getPageIndicators()
})

const pageUp = () => {
    if (props.currentPage + props.pageIncrement < pageTotal.value) {
        emit('pageUp', props.pageIncrement)
    }
}

const pageDown = () => {
    if (props.currentPage - props.pageIncrement >= 0) {
        emit('pageDown', (props.pageIncrement * -1))
    }
}

</script>

<template>
    <div class="page-nav-main">
        <img 
            src="/aspire/static/assets/icon-chevron-left-blue.png"
            @click="pageDown"
        />
        <div>
            <span 
                v-for="item of pageIndicators"
                :class="item === (currentPage / props.pageIncrement) + 1 ? 'indicator indicator-bold' : 'indicator indicator-muted'"
                @click="() => emit('pageSelect', item, props.pageIncrement)"
            >
                {{ item }}
            </span>
        </div>
        <img 
            src="/aspire/static/assets/icon-chevron-right-blue.png"
            @click="pageUp"
        />
    </div>
    
</template>

<style scoped>
.page-nav-main {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    width: 35%;
    height: 100%;
    column-gap: 0.25rem;
}
.page-nav-main > img {
    aspect-ratio: 1/1;
    height: 100%;
}
.indicator {
    font-size: larger;
    padding: 0.5rem;
    color: var(--core-primary);

}
.indicator-bold {
    text-decoration: underline;
    font-weight: bold;
    background: var(--core-primary);
    color: var(--text-color-alt);
    border-radius: 25%;
}
</style>
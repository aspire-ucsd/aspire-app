<script setup>
/* eslint-disable */
import { ref, defineProps, computed, reactive, defineEmits, defineModel } from 'vue';

const props = defineProps(['comment'])


const parseComment = computed(() => {
    if (props.comment.type === 'text') {
        return props.comment.content
    } 
    else {
        const splitContent = props.comment.content.split('|')
        let result = {};

        for (let i = 0; i < splitContent.length; i += 2) {
            result[splitContent[i]] = splitContent[i + 1];
        }
        if (result.data) {
            result.data = JSON.parse(result.data)
        }
        return result
    }
})

const progressBarStyle = computed(() => {
    const proportion = (parseComment.value.data.filter(vote => vote === 'approved').length / parseComment.value.data.length) * 100

    return {
        proportion: proportion,
    };
})

</script>

<template>
    <div v-if="props.comment?.type === 'text'">
        <p>{{ parseComment }}</p>
    </div>
    <div 
        class="comment"
        v-if="props.comment?.type === 'update' && !parseComment.data_type"
    >
        <p>{{ parseComment.msg }}</p>
    </div>
    <div 
        class="comment"
        v-if="props.comment?.type === 'approve_vote' || props.comment?.type === 'reject_vote'"
    >
        <p>{{ parseComment.msg }}</p>
    </div>
    <div 
        class="comment"
        v-if="props.comment?.type === 'update' && parseComment.data_type === 'entity_data'"
    >
        <p>{{ parseComment.msg }}</p>
        <hr />
        <div class="entity-data">
            <div class="to-from-box">
                <h3><u>From</u></h3>
                <br />
                <div v-for="[key, value] of Object.entries(parseComment.data.old)">
                    <p><strong>{{ key.charAt(0).toUpperCase() + key.slice(1) }}: </strong><br />{{ value }}</p>
                    <br />
                </div>
            </div>
            <hr />
            <div class="to-from-box">
                <h3><u>To</u></h3>
                <br />
                <div v-for="[key, value] of Object.entries(parseComment.data.new)">
                    <p><strong>{{ key.charAt(0).toUpperCase() + key.slice(1) }}: </strong><br />{{ value }}</p>
                    <br />
                </div>
            </div>
        </div>
    </div>
    <div 
        class="proposed-content"
        v-if="props.comment?.type === 'proposal' && parseComment.data_type === 'entity_data'"
    >
        <p>{{ parseComment.msg }}</p>
        <hr />
        <div class="entity-data">
            <div class="to-from-box">
                <div v-for="[key, value] of Object.entries(parseComment.data)">
                    <p><strong>{{ key.charAt(0).toUpperCase() + key.slice(1) }}: </strong><br />{{ value }}</p>
                    <br />
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>

.comment {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: white;
}
.comment > hr {
    width: 100%;
}
.entity-data {
    display: flex;
    width: 100%;
    align-items: space-evenly;
    justify-content: space-evenly;
}
.to-from-box {
    padding: 0.5rem;
}
</style>
<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { SwitchRoot, SwitchThumb } from 'radix-vue'

const props = defineProps(["modalOpen", "formMode"])
const emit = defineEmits(["addCollection", "updateOpen"])

const collectionForm = ref({})
const typeToggle = ref(false)

function cancel() {
    emit("updateOpen", false)
    collectionForm.value = {}
}

function submit() {
    collectionForm.value.type = typeToggle.value ? "container": "module"
    emit("addCollection", collectionForm.value)
    emit("updateOpen", false)
    collectionForm.value = {}
}

</script>

<template>
    <div v-if="props.modalOpen" class="collection-modal">
        <div class="collection-form">
            <h4>Add a New Concept Collection</h4>
            <hr style="border-color: var(--gold-line-color); margin-bottom: .5rem;"/>
            <form class="form-contents">
                <label class="required-input" for="collection-label">Label</label>
                <input 
                    id="collection-label" 
                    :value="collectionForm.label" 
                    @input="event => {collectionForm.label = event.target.value}"
                    placeholder="Label must exceed 4 characters"
                />
                <br />
                <label for="collection-summary">Content Summary</label>
                <textarea id="collection-label" :value="collectionForm.content_summary" @input="event => {collectionForm.content_summary = event.target.value}"/>
                <br/>
                <div class="type-toggle-box">
                    <label>Type: {{ typeToggle ? "Container": "Module" }}</label>
                    <SwitchRoot
                        id="type-toggle"
                        v-model:checked="typeToggle"
                        class="type-toggle-root"
                        >
                    <SwitchThumb
                            class="type-toggle-thumb"
                        />
                    </SwitchRoot>

                </div>
                <br/>
            </form>
            <button @click="cancel">Cancel</button>
            <button v-if="collectionForm.label && collectionForm.label.length > 3" @click="submit">Submit</button>
        </div>
    </div>
</template>

<style>

.type-toggle-box {
    display: flex;
    flex-direction: column;
    column-gap: 2px;
    align-items: flex-start;
    width: 100%
}
.type-toggle-root {
    width: 42px;
    height: 18px;
    position: relative;
    border-radius: 9px;
    background-color: var(--bg-color);
    border: 2px solid var(--core-primary);
}
.type-toggle-root[data-state=checked] {
    background-color: var(--core-primary);
    cursor: default;
}
.type-toggle-thumb {
    display: block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    transform:translateX(0.5);
    transition: transform 1s ease-in-out;
    background-color: var(--gold-line-color);
}
.type-toggle-thumb[data-state=checked] {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    transform:translateX(26px);
    transition: transform .3s ease-in-out;
}
.type-toggle-thumb[data-state=unchecked] {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    transform:translateX(0px);
    transition: transform .3s ease-in-out;
}
.required-input{
    position: relative;
}
.required-input:after {
    content:" *";
    color: red;
    display: inline;
}
.collection-modal {
    position: fixed;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(211, 211, 211, 0.565);
    z-index: 999;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
}
.collection-form {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    border-radius: 5px;
    border: 1px solid var(--gold-line-color);
    background-color: white;
}
.form-contents{
    display: flex;
    flex-direction: column;
}
</style>
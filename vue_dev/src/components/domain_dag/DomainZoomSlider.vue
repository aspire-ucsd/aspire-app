<script setup>
import { defineModel } from 'vue'
import { SliderRange, SliderRoot, SliderThumb, SliderTrack } from 'radix-vue'

// wish I had looked into v-model sooner, would've cleaned up some of my previous code dramatically...
// TODO: update domainDag to use v-model where props and emits are used
const zoomLevel = defineModel('zoomLevel', {
    get(value) {
        return [value]
    },
    set(value){
        return value[0]
    }
})

</script>

<template>
    <SliderRoot
        class="slider-root"
        v-model="zoomLevel"
        :max="3"
        :min="0.1"
        :step="0.1"
        :default-value='[1]'
        
    >
        <SliderTrack class="slider-track">
            <SliderRange class="slider-range"/>
        </SliderTrack>
        <SliderThumb
        class="slider-thumb"
        aria-label="zoom"
        v-bind:title='zoomLevel * 100 + "%"'
        />
    </SliderRoot>
</template>

<style>
.slider-root {
    display: flex;
    width: 100%;
    height: 2rem;
    align-items: center;
}
.slider-track{
    width: 100%;
    height: 5px;
    background-color: lightgray;
    border-radius: 2.5px;
}
.slider-range {
    position: absolute;
    background-color: grey;
    height: 5px;
    border-radius: 2.5px;
}
.slider-thumb {
    background-color: var(--accent-primary);
    width: 14px;
    height: 14px;
    border-radius: 50%;
}
</style>

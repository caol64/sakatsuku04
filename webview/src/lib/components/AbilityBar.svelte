<script lang="ts">
    let { abilities = [0, 0, 0], is100 = false } = $props();

    let current = $derived.by(() => `${is100 ? abilities[0] : Math.round(abilities[0] / 65535 * 100)}%`);
    let currentMax = $derived.by(() => `${is100 ? abilities[1] : Math.round((abilities[1] - abilities[0]) / 65535 * 100)}%`);
    let max = $derived.by(() => `${is100 ? abilities[2] : Math.round((abilities[2] - abilities[1]) / 65535 * 100)}%`);
</script>

<div class="flex w-full h-3 bg-gray-200 overflow-hidden dark:bg-neutral-700">
    <div class="flex flex-col justify-center overflow-hidden bg-green-200 text-xs text-white text-center whitespace-nowrap" style="width: {current}"></div>
    <div class="flex flex-col justify-center overflow-hidden bg-amber-400 text-xs text-white text-center whitespace-nowrap" style="width: {currentMax}"></div>
    <div class="flex flex-col justify-center overflow-hidden bg-sky-300 text-xs text-white text-center whitespace-nowrap" style="width: {max}"></div>
</div>

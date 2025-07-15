<script lang="ts">
    let { values = [0, 0, 0], pos = 0 } = $props();
</script>

<div class="flex flex-col items-center my-1 rounded-lg w-full space-y-1 bg-white dark:bg-gray-700 p-2">
    <div class="flex justify-center space-x-1 w-20 h-24 items-end">
        {#each values as val, i}
            <div class="w-4 h-full border border-gray-300 flex items-end">
                <div class={i === 0 ? 'bg-green-500' : i === 1 ? (pos === 0 ? 'bg-red-500' : 'bg-blue-500') : 'bg-yellow-400'}
                    style="height: {(val / 31) * 100}%; width: 100%"></div>
            </div>
        {/each}
    </div>
    <div class="border-t border-gray-100 w-20 mt-1"></div>
    <div class="flex justify-center text-gray-500 text-xs font-bold tracking-wide">
        ODC
    </div>
</div>

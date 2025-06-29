<script lang="ts">
    export let values = [0.8, 0.6, 0.9]; // 每个条的高度百分比
</script>

<div class="flex flex-col items-center p-2 rounded w-20 space-y-1">
    <div class="flex space-x-1 h-24 items-end">
        {#each values as val, i}
            <div class="w-4 h-full border border-gray-300 flex items-end">
                <div class={i === 0 ? 'bg-green-500' : i === 1 ? 'bg-blue-500' : 'bg-yellow-400'}
                     style="height: {val * 100}%; width: 100%"></div>
            </div>
        {/each}
    </div>
    <div class="border-t border-gray-100 w-full mt-1"></div>
    <div class="flex justify-center text-gray-500 text-xs font-bold tracking-wide">
        ODC
    </div>
</div>

<script lang="ts">
    import Forward from "$lib/icons/Forward.svelte";
    import { type Scout } from "$lib/models";
    import { getRank, getTeamData } from "$lib/utils";
    import HStack from "./Stack/HStack.svelte";

    let { selectedScout, showDrawer = $bindable() }: {selectedScout: Scout, showDrawer: boolean} = $props();

    function showBScout() {
        showDrawer = true;
    }
</script>

<div class="h-fit bg-gray-50 dark:bg-gray-700 rounded-2xl shadow p-6 flex flex-col space-y-4 text-sm">
    {#if selectedScout.id && selectedScout.id >= 20000}
        <div class="flex justify-center">
            <button onclick={showBScout} class="cursor-pointer flex items-center">
                查看数据库
                <Forward />
            </button>
        </div>
    {/if}
    <p class="font-medium">
        年龄
        <span class="pl-8 text-sm">
            {selectedScout.age}
        </span>
    </p>
    <p class="font-medium">
        合约
        <span class="pl-8 text-sm">
            {selectedScout.contractYears ?? 0} / {selectedScout.offerYears} 年
        </span>
    </p>
    {#if selectedScout.salaryHigh || selectedScout.salaryLow}
        <p class="font-medium">
            年薪
            {#if selectedScout.salaryHigh}
                <span class="pl-8 text-sm">
                    {selectedScout.salaryHigh} 亿
                </span>
            {/if}
            <span class="pl-{selectedScout.salaryHigh ? '2' : '8'} text-sm">{selectedScout.salaryLow} 万</span>
        </p>
    {/if}
    {#if selectedScout.rank !== undefined && selectedScout.rank >= 0}
        <p class="font-medium">
            等级
            <span class="pl-8 text-sm">
                {getRank(selectedScout.rank)}
            </span>
        </p>
    {/if}
    {#if selectedScout.exclusivePlayers?.length}
        <p class="font-medium">专有球员</p>
        <div class="ml-8 space-y-2 text-sm font-medium">
            {#each selectedScout.exclusivePlayers as item}
                <HStack>
                    <p class="w-[100px]">{item.name}</p>
                    {#if item.teamId != null}
                        <p class="ml-4">{getTeamData()[item.teamId]}</p>
                        <p class="ml-4">{item.age}岁</p>
                    {/if}
                </HStack>
            {/each}
        </div>
    {/if}
    {#if selectedScout.simiExclusivePlayers?.length}
        <p class="font-medium">半专有球员</p>
        <div class="ml-8 space-y-2 text-sm font-medium">
            {#each selectedScout.simiExclusivePlayers as item}
                <HStack>
                    <p class="w-[100px]">{item.name}</p>
                    {#if item.teamId != null}
                        <p class="ml-4">{getTeamData()[item.teamId]}</p>
                        <p class="ml-4">{item.age}岁</p>
                    {/if}
                </HStack>
            {/each}
        </div>
    {/if}
</div>

<script lang="ts">
    import Avatar from "$lib/icons/Avatar.svelte";
    import { type Scout } from "$lib/models";
    import { getRank, getRegion, getTeamData, toHex } from "$lib/utils";
    import AbilityBar from "./AbilityBar.svelte";
    import PositionGrid from "./PositionGrid.svelte";
    import RadarChart4 from "./RadarChart4.svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import WorldMap from "./WorldMap.svelte";
    import ability from "$locales/scout_abilities_zh.json";

    let { selectedScout }: { selectedScout: Scout } = $props();

    let abilityPairs = $derived(
        ability.map((label, i) => ({
            label,
            value: [0, 0, selectedScout.abilities[i]]
        }))
    );
</script>

<VStack className="w-1/5 mx-1">
    <div class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
        <p class="flex items-center justify-between">
            姓名
            <span class="flex-1 pl-8 text-sm select-text">{selectedScout?.name}</span>
        </p>
        <p>
            ID
            <span class="pl-8 text-sm select-text">{selectedScout?.id && toHex(selectedScout.id, 4)}</span>
        </p>
        <p>
            出生地
            <span class="pl-8 text-sm">{selectedScout?.born && getRegion(selectedScout?.born)}</span>
        </p>
        <p>
            年龄
            <span class="pl-8 text-sm">{selectedScout?.age}</span>
        </p>
        <p>
            年薪
            {#if selectedScout?.salaryHigh}
                <span class="pl-8 text-sm">
                    {selectedScout?.salaryHigh} 亿
                </span>
            {/if}
            <span class="pl-{selectedScout?.salaryHigh ? '2' : '8'} text-sm">{selectedScout?.salaryLow} 万</span>
        </p>
        <p>
            等级
            <span class="pl-8 text-sm">{selectedScout?.rank && getRank(selectedScout.rank)}</span>
        </p>
        <p>擅长地区</p>
        <div class="pl-4 text-sm text-left">
            <span>{getRegion(selectedScout?.nati1 ?? 0)}</span>
            {#if selectedScout?.nati2}
                <span>{getRegion(selectedScout?.nati2)}</span>
            {/if}
        </div>
        {#if selectedScout?.exclusivePlayers && selectedScout.exclusivePlayers.length > 0}
            <div class="flex items-center gap-x-2">
                <p>专有球员</p>
                <Avatar />
            </div>
            <div class="pl-4 text-sm text-left">
                {#each selectedScout?.exclusivePlayers as item}
                    <div>
                        <p class="w-[100px]">{item.name}</p>
                        <HStack>
                            {#if item.teamId != null}
                                <p class="ml-4">{getTeamData()[item.teamId]}</p>
                                <p class="ml-4">{item.age}岁</p>
                            {/if}
                        </HStack>
                    </div>
                {/each}
            </div>
        {/if}
        {#if selectedScout?.simiExclusivePlayers && selectedScout.simiExclusivePlayers.length > 0}
            <div class="flex items-center gap-x-2">
                <p>半专有球员</p>
                <Avatar />
            </div>
            <div class="pl-4 text-sm text-left">
                {#each selectedScout.simiExclusivePlayers as item}
                    <div>
                        <p class="w-[100px]">{item.name}</p>
                        <HStack>
                            {#if item.teamId != null}
                                <p class="ml-4">{getTeamData()[item.teamId]}</p>
                                <p class="ml-4">{item.age}岁</p>
                            {/if}
                        </HStack>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</VStack>
<VStack className="w-3/10 mx-1">
    <RadarChart4 abilities={selectedScout?.hexagon ?? Array(4).fill(0)} />
    <PositionGrid aposEval={selectedScout?.aposEval} />
    <WorldMap />
    <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
        <p>{selectedScout?.eval}</p>
    </div>
</VStack>

<VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
    {#each abilityPairs as { label, value }}
        <HStack className="items-center">
            <span class="w-50 text-sm">{label}</span>
            {#if value}
                {@const tooltipText = `${value[2]}`}
                <Tooltip text={tooltipText} className="w-full">
                    <AbilityBar abilities={value} is100={true} />
                </Tooltip>
            {/if}
        </HStack>
    {/each}
</VStack>

<script lang="ts">
    import type { BScout } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import { getRegion, getRank } from "$lib/utils";
    import ability from "$locales/scout_abilities_zh.json";
    import AbilityBar from "./AbilityBar.svelte";
    import RadarChart4 from "./RadarChart4.svelte";
    import PositionGrid from "./PositionGrid.svelte";
    import Tooltip from "./Tooltip.svelte";
    import WorldMap from "./WorldMap.svelte";

    let { selectedScout = 0 } = $props();

    let bScout: BScout = $state({abilities: [], hexagon: []});
    let stats = $state(Array(4).fill(0));

    let abilityPairs = $derived(
        ability.map((label, i) => ({
            label,
            value: [0, 0, bScout.abilities[i]]
        }))
    );

    async function fetchBScout() {
        if (window.pywebview?.api?.get_bscout) {
            bScout = await window.pywebview.api.get_bscout(selectedScout);
            stats = bScout.hexagon;
        } else {
            alert('API 未加载');
        }
    }

    onMount(async () => {
        // fetchBScout();
	});

    $effect(() => {
        if(selectedScout) {
            fetchBScout();
        }
    });

</script>

<VStack className="w-1/5 mx-1">
    <div class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
        <p class="flex items-center justify-between select-text">
            姓名
            <span class="flex-1 pl-8 text-sm">{bScout?.name}</span>
        </p>
        <p>
            出生地
            <span class="pl-8 text-sm">{getRegion(bScout?.born)}</span>
        </p>
        <p>
            年龄
            <span class="pl-8 text-sm">{bScout?.age}</span>
        </p>
        <p>
            年薪
            {#if bScout?.salaryHigh}
                <span class="pl-8 text-sm">
                    {bScout?.salaryHigh} 亿
                </span>
            {/if}
            <span class="pl-{bScout?.salaryHigh ? '2' : '8'} text-sm">{bScout?.salaryLow} 万</span>
        </p>
        <p>
            等级
            <span class="pl-8 text-sm">{getRank(bScout?.rank)}</span>
        </p>
        <p>
            出现所需声望
            <span class="pl-8 text-sm">{bScout?.signingDifficulty}</span>
        </p>
        <p>擅长地区</p>
        <div class="pl-4 text-sm text-left">
            <span>{getRegion(bScout?.nati1)}</span>
            {#if bScout?.nati2}
                <span>{getRegion(bScout?.nati2)}</span>
            {/if}
        </div>
        <p>隐藏属性</p>
        <div class="pl-4 grid grid-cols-2 gap-x-1 text-sm text-left">
            <div><span>野心</span><span class="pl-3">{bScout?.ambition}</span></div>
            <div><span>毅力</span><span class="pl-3">{bScout?.persistence}</span></div>
        </div>
        {#if bScout?.exclusivePlayers && bScout.exclusivePlayers.length > 0}
            <p>专有球员</p>
            <div class="pl-4 text-sm text-left">
                {#each bScout?.exclusivePlayers as item}
                    <div>{item}</div>
                {/each}
            </div>
        {/if}
        {#if bScout?.simiExclusivePlayers && bScout.simiExclusivePlayers.length > 0}
            <p>半专有球员</p>
            <div class="pl-4 text-sm text-left">
                {#each bScout.simiExclusivePlayers as item}
                    <div>{item}</div>
                {/each}
            </div>
        {/if}
    </div>
</VStack>
<VStack className="w-3/10 mx-1">
    <RadarChart4 abilities={stats} />
    <PositionGrid aposEval={bScout.aposEval} />
    <WorldMap />
    <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
        <p>{bScout?.eval}</p>
    </div>
</VStack>

<VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
    {#each abilityPairs as { label, value }}
        <HStack className="items-center">
            <span class="w-24 text-sm">{label}</span>
            {#if value}
                {@const tooltipText = `${value[2]}`}
                <Tooltip text={tooltipText} className="w-full">
                    <AbilityBar abilities={value} is100={true} />
                </Tooltip>
            {/if}
        </HStack>
    {/each}
</VStack>

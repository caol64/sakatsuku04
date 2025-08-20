<script lang="ts">
    import type { BScout } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import { getRegion } from "$lib/utils";
    import ability from "$locales/scout_abilities_zh.json";
    import AbilityBar from "./AbilityBar.svelte";
    import RadarChart4 from "./RadarChart4.svelte";
    import PositionGrid from "./PositionGrid.svelte";

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
    </div>
</VStack>
<VStack className="w-3/10 mx-1">
    <RadarChart4 abilities={stats} />
    <PositionGrid aposEval={bScout.aposEval} />
    <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
        <p>hhhh</p>
    </div>
</VStack>

<VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
    {#each abilityPairs as { label, value }}
        <HStack className="items-center">
            <span class="w-24 text-sm">{label}</span>
            {#if value}
                <AbilityBar abilities={value} is100={true} />
            {/if}
        </HStack>
    {/each}
</VStack>

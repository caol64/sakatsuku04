<script lang="ts">
    import type { Coach } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import { getRefreshFlag, getSelectedTab, setIsLoading, setRefreshFlag } from "$lib/globalState.svelte";
    import ability from "$locales/mcoach_abilities_zh.json";
    import Close from "$lib/icons/Close.svelte";
    import BCoachDetails from "./BCoachDetails.svelte";
    import Airplane from "$lib/icons/Airplane.svelte";
    import Tooltip from "./Tooltip.svelte";
    import AbilityBar from "./AbilityBar.svelte";
    import CoachesViewDetails from "./CoachesViewDetails.svelte";
    import Component from "$lib/icons/Component.svelte";

    let myCoaches: Coach[] = $state([]);
    let selectedId = $state(0);
    let selectedType = $state(0);
    let selectedCoach: Coach = $state({id: 0, name: "", abilities: [], bringAbroads: []});
    let showDrawer = $state(false);

    let abilityPairs = $derived(
        ability.map((label, i) => ({
            label,
            value: [0, 0, selectedCoach.abilities[i]]
        }))
    );

    async function fetchMyCoaches() {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_my_coaches) {
                myCoaches = await window.pywebview.api.fetch_my_coaches(selectedType);
                if (myCoaches && myCoaches.length > 0) {
                    selectedId = myCoaches[0].id;
                    await fetchMyCoach(selectedId);
                }
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    async function fetchMyCoach(id: number) {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_coach) {
                selectedCoach = await window.pywebview.api.fetch_coach(id, selectedType);
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    onMount(async () => {
        fetchMyCoaches();
	});

    async function onCoachTabClick(type: number) {
        if (selectedType !== type) {
            selectedType = type;
            await fetchMyCoaches();
        }
    }

    async function onCoachClick(id: number) {
        if (selectedId !== id) {
            selectedId = id;
            await fetchMyCoach(selectedId);
        }
    }

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Coaches") {
            try {
                fetchMyCoaches();
            } finally {
                setRefreshFlag(false);
            }
        }
    });

    function toggleDrawer() {
        showDrawer = !showDrawer;
    }


</script>

<HStack className="flex-1 overflow-hidden m-2.5">
    <VStack className="w-1/5 mr-1">
        <HStack className="space-x-4 mb-2 mx-2">
            <button onclick={() => onCoachTabClick(0)} class="badges">已签约</button>
            <button onclick={() => onCoachTabClick(1)} class="badges">待签约</button>
        </HStack>
        {#if myCoaches && myCoaches.length > 0}
            <div class="sidebar">
                {#each myCoaches as item}
                    <button
                        onclick={() => onCoachClick(item.id)}
                        class={selectedId === item.id ? "activate" : ""}
                    >
                        <span class="flex items-center justify-between w-full">
                            {item.name}
                            <HStack>
                                <div class="mr-2 w-3.5 h-3.5 flex items-center justify-center">
                                    {#if item.spSkill !== undefined && item.spSkill !== null}
                                        <Component />
                                    {/if}
                                </div>
                                <div class="mr-2 w-3.5 h-3.5 flex items-center justify-center">
                                    {#if item.isBringAbroad}
                                        <Airplane />
                                    {/if}
                                </div>
                            </HStack>
                        </span>
                    </button>
                {/each}
            </div>
        {:else}
            <div class="border text-sm border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
                空空如也
            </div>
        {/if}
    </VStack>
    {#if selectedType === 0}
        <VStack className="w-1/2 mx-1">
            <CoachesViewDetails selectedCoach={selectedCoach} bind:showDrawer={showDrawer} />
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
    {:else}
        <VStack className="grow ml-8 space-y-2">
            <CoachesViewDetails selectedCoach={selectedCoach} bind:showDrawer={showDrawer} />
        </VStack>
    {/if}
    {#if selectedCoach?.id && selectedCoach.id >= 20000}
        <div class="fixed top-0 left-0 h-full w-full bg-white dark:bg-gray-800 shadow-lg transition-transform duration-300 z-50"
            class:translate-x-0={showDrawer}
            class:translate-x-full={!showDrawer}>
            <HStack className="flex-1 h-full overflow-hidden m-2.5">
                <VStack className="w-1/5">
                    <button onclick={toggleDrawer} class="cursor-pointer">
                        <Close />
                    </button>
                </VStack>
                <BCoachDetails selectedCoach={selectedCoach.id} />
            </HStack>
        </div>
    {/if}
</HStack>


<style lang="postcss">
    @reference "tailwindcss";
    .sidebar {
        @apply w-full text-gray-900 bg-white border border-gray-200 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white overflow-y-auto text-xs;
    }
    .sidebar button {
        @apply relative cursor-pointer inline-flex items-center w-full px-4 py-1 text-sm font-medium border-b border-gray-200 rounded-t-lg hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-2 focus:ring-blue-700 focus:text-blue-700 dark:border-gray-600 dark:hover:bg-gray-600 dark:hover:text-white dark:focus:ring-gray-500 dark:focus:text-white;
    }
    .activate {
        @apply bg-gray-100 text-blue-700 dark:bg-gray-600 dark:text-white;
    }
    .badges {
        @apply cursor-pointer bg-blue-100 text-blue-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-sm dark:bg-blue-900 dark:text-blue-300;
    }
</style>

<script lang="ts">
    import type { Scout } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import teamsData from "$locales/teams_zh.json";
    import { getRefreshFlag, getSelectedTab, setIsLoading, setRefreshFlag } from "$lib/globalState.svelte";

    let myScouts: Scout[] = $state([]);
    let selectedScoutId = $state(0);
    let selectedType = $state(0);
    let selectedScout: Scout | null = $derived.by(() => {
        if (!myScouts || myScouts.length === 0) return null;
        return myScouts.find(a => a.id === selectedScoutId) ?? null;
    });

    async function fetchMyScouts() {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_my_scouts) {
                myScouts = await window.pywebview.api.fetch_my_scouts(selectedType);
                if (myScouts && myScouts.length > 0) {
                    selectedScoutId = myScouts[0].id;
                }
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    onMount(async () => {
        fetchMyScouts();
	});

    async function onScoutTabClick(type: number) {
        if (selectedType !== type) {
            selectedType = type;
            await fetchMyScouts();
        }
    }

    async function onScoutClick(id: number) {
        if (selectedScoutId !== id) {
            selectedScoutId = id;
        }
    }

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Scouts") {
            try {
                fetchMyScouts();
            } finally {
                setRefreshFlag(false);
            }
        }
    });
</script>

<HStack className="flex-1 overflow-hidden m-2.5">
    <VStack className="w-1/5 mr-1">
        <HStack className="space-x-4 mb-2 mx-2">
            <button onclick={() => onScoutTabClick(0)} class="badges">已签约</button>
            <button onclick={() => onScoutTabClick(1)} class="badges">待签约</button>
        </HStack>
        {#if myScouts && myScouts.length > 0}
            <div class="sidebar">
                {#each myScouts as item}
                    <button
                        onclick={() => onScoutClick(item.id)}
                        class={selectedScoutId === item.id ? "activate" : ""}
                    >
                        <span class="flex items-center justify-between w-full">
                            {item.name}
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
    <div class="grow bg-gray-50 dark:bg-gray-700 rounded-2xl shadow p-6 flex flex-col space-y-2 mx-8 text-sm font-medium">
        {#if selectedScout?.exclusivePlayers?.length}
            <p>专有球员</p>
            <div class="ml-8">
                {#each selectedScout.exclusivePlayers as item}
                    <HStack>
                        <p class="w-[100px]">{item.name}</p>
                        {#if item.teamId != null}
                            <p class="ml-4">{teamsData[item.teamId]}</p>
                            <p class="ml-4">{item.age}岁</p>
                        {/if}
                    </HStack>
                {/each}
            </div>
        {/if}
        {#if selectedScout?.simiExclusivePlayers?.length}
            <p>半专有球员</p>
            <div class="ml-8">
                {#each selectedScout.simiExclusivePlayers as item}
                    <HStack>
                        <p class="w-[100px]">{item.name}</p>
                        {#if item.teamId != null}
                            <p class="ml-4">{teamsData[item.teamId]}</p>
                            <p class="ml-4">{item.age}岁</p>
                        {/if}
                    </HStack>
                {/each}
            </div>
        {/if}
    </div>
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

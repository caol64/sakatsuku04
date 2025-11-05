<script lang="ts">
    import type { Sponsors } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import sponsors from "$locales/sponsor_zh.json";
    import { gameVersion, getRefreshFlag, getSelectedTab, setIsLoading, setRefreshFlag } from "$lib/globalState.svelte";
    import Airplane from "$lib/icons/Airplane.svelte";
    import Tooltip from "./Tooltip.svelte";
    import { getTeamData } from "$lib/utils";

    let mySponsors: Sponsors[] = $state([]);
    let selectedId = $state(0);
    let selectedType = $state(0);
    let selectedSponsor: Sponsors | null = $derived.by(() => {
        if (!mySponsors || mySponsors.length === 0) return null;
        return mySponsors.find(a => a.id === selectedId) ?? null;
    });

    async function fetchMySponsors() {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_my_sponsors) {
                mySponsors = await window.pywebview.api.fetch_my_sponsors(selectedType);
                if (mySponsors && mySponsors.length > 0) {
                    selectedId = mySponsors[0].id;
                }
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    onMount(async () => {
        fetchMySponsors();
	});

    async function onSponsorTabClick(type: number) {
        if (selectedType !== type) {
            selectedType = type;
            await fetchMySponsors();
        }
    }

    async function onSponsorClick(id: number) {
        if (selectedId !== id) {
            selectedId = id;
        }
    }

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Sponsors") {
            try {
                fetchMySponsors();
            } finally {
                setRefreshFlag(false);
            }
        }
    });
</script>

<HStack className="flex-1 overflow-hidden m-2.5">
    <VStack className="w-1/5 mr-1">
        <HStack className="space-x-4 mb-2 mx-2">
            <button onclick={() => onSponsorTabClick(0)} class="badges">已签约</button>
            <button onclick={() => onSponsorTabClick(1)} class="badges">待签约</button>
        </HStack>
        {#if mySponsors && mySponsors.length > 0}
            <div class="sidebar">
                {#each mySponsors as item}
                    <button
                        onclick={() => onSponsorClick(item.id)}
                        class={selectedId === item.id ? "activate" : ""}
                    >
                        <span class="flex items-center justify-between w-full">
                            {sponsors[item.id]}
                            {#if item.bringAbroads && item.bringAbroads.length > 0}
                                {@const tooltipText = item.bringAbroads
                                    .map(i => {
                                        const name = getTeamData(gameVersion)[i.id - 255];
                                        return i.type === 1 ? `${name}(C)` : name;
                                    })
                                    .join("<br>")}
                                <div class="mx-2">
                                    <Tooltip text={tooltipText} width="200px">
                                        <Airplane />
                                    </Tooltip>
                                </div>
                            {/if}
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
    {#if mySponsors && mySponsors.length > 0}
        <VStack className="grow ml-8 space-y-2">
            <div class="h-fit bg-gray-50 dark:bg-gray-700 rounded-2xl shadow p-6 flex flex-col space-y-4 text-sm">
                <p class="font-medium">
                    金额
                    {#if selectedSponsor?.amountHigh}
                        <span class="pl-8 text-sm">
                            {selectedSponsor?.amountHigh} 亿
                        </span>
                    {/if}
                    <span class="pl-{selectedSponsor?.amountHigh ? '2' : '8'} text-sm">{selectedSponsor?.amountLow} 万</span>
                </p>
                <p class="font-medium">
                    合约
                    <span class="pl-8 text-sm">
                        {selectedSponsor?.contractYears} / {selectedSponsor?.offerYears} 年
                    </span>
                </p>
                {#if selectedSponsor?.bringAbroads && selectedSponsor?.bringAbroads.length > 0}
                    <p class="font-medium">留学/集训地</p>
                    {#each selectedSponsor.bringAbroads as abr}
                        <p class="font-medium pl-8">{`${getTeamData(gameVersion)[abr.id - 255]}${abr.type === 1 ? "(C)" : ""}${abr.isEnabled ? " 已获得" : ""}`}</p>
                    {/each}
                {/if}
            </div>
        </VStack>
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

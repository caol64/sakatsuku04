<script lang="ts">
    import type { Abroad } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import teamsData from "$locales/teams_zh.json";
    import condType from "$locales/cond_type_zh.json";
    import townType from "$locales/town_type_zh.json";
    import { getRefreshFlag, getSelectedTab, setIsLoading, setRefreshFlag } from "$lib/globalState.svelte";
    import { sortedAbilities } from "$lib/utils";
    import AbrAbilityBar from "./AbrAbilityBar.svelte";
    import Check from "$lib/icons/Check.svelte";

    let selectedType = $state(0);
    let selectedIndex = $state(0);
    let abroads: Abroad[] = $state([]);
    let selectedAbroad: Abroad = $state({ id: 0, isEnabled: false, abrUp: [], abrUprate: [], abrDays: 0 });
    let currentCondType = $derived.by(() => {
        const cond = selectedAbroad.cond;
        if (cond) {
            return condType[cond.id - 1];
        }
        return "";
    });
    let currentCondValue = $derived.by(() => {
        const cond = selectedAbroad.cond;
        if (cond) {
            if (cond.id === 2) {
                return cond.cond.map((i) => townType[Number(i)]);
            } else if (cond.id === 7) {
                return cond.cond;
            } else {
                return cond.cond;
            }
        }
        return [];
    });
    let abilityPairs = $derived(
        sortedAbilities.map((label, i) => ({
            label,
            value: selectedAbroad.abrUp[i]
        }))
    );
    let currentBestTime = $derived.by(() => {
        if (selectedAbroad.abrDays != 0) {
            return fixedTimeZh[selectedAbroad.abrDays - 1];
        } else {
            const abrUprate = selectedAbroad.abrUprate;
            if (abrUprate) {
                const index = getMaxDiffIndex([abrUprate[0], abrUprate[1], abrUprate[2]]);
                return bestTimeZh[index];
            }
        }
        return "";
    });
    let currentGrowType = $derived.by(() => {
        const abrUprate = selectedAbroad.abrUprate;
        if (abrUprate) {
            return getGrowType([abrUprate[3], abrUprate[4]]);
        }
        return "";
    });

    async function fetchAbroads() {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_abroads) {
                abroads = await window.pywebview.api.fetch_abroads(selectedType);
                if (abroads && abroads.length > 0) {
                    selectedIndex = 0;
                    await fetchOneAbroad();
                }
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    async function fetchOneAbroad() {
        if (window.pywebview?.api?.fetch_one_abroad) {
            selectedAbroad = await window.pywebview.api.fetch_one_abroad(selectedIndex, selectedType);
        } else {
            alert('API 未加载');
        }
    }

    onMount(async () => {
        fetchAbroads();
	});

    async function onAbroadTabClick(type: number) {
        if (selectedType !== type) {
            selectedType = type;
            await fetchAbroads();
        }
    }

    async function onSidebarClick(id: number) {
        if (selectedIndex !== id) {
            selectedIndex = id;
            await fetchOneAbroad();
        }
    }

    function getMaxDiffIndex(input: [number, number, number]): number {
        const base = [60, 100, 150];
        const diffs = input.map((val, i) => val - base[i]);
        if (diffs[0] === diffs[1] && diffs[1] === diffs[2]) {
            return 1;
        }
        const maxDiff = Math.max(...diffs);
        return diffs.indexOf(maxDiff);
    }

    function getGrowType(input: [number, number]): string {
        if (input[0] >= 90) {
            return "实能";
        } else if (input[1] >= 90) {
            return "界限";
        } else {
            return "平均";
        }
    }

    const bestTimeZh = ["短期", "标准", "长期"];
    const fixedTimeZh = ["半年限定", "一年限定", "两年限定"];

</script>

<HStack className="flex-1 overflow-hidden m-2.5">
    <VStack className="w-1/5 mr-1">
        <HStack className="space-x-4 mb-2 mx-2">
            <button onclick={() => onAbroadTabClick(0)} class="badges">留学地</button>
            <button onclick={() => onAbroadTabClick(1)} class="badges">集训地</button>
        </HStack>
        {#if abroads && abroads.length > 0}
            <div class="sidebar">
                {#each abroads as item, index}
                    <button
                        onclick={() => onSidebarClick(index)}
                        class={selectedIndex === index ? "activate" : ""}
                    >
                        <span class="flex items-center justify-between w-full">
                            {teamsData[item.id - 255]}
                            {#if item.isEnabled}
                                <div class="mx-2"><Check /></div>
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

    <VStack className="w-1/4 h-full overflow-auto mx-2 pl-1">
        {#each abilityPairs as { label, value }}
            <HStack className="items-center">
                <span class="w-24 text-sm">{label}</span>
                {#if value != null}
                    <AbrAbilityBar value={value} />
                {/if}
            </HStack>
        {/each}
    </VStack>

    <VStack className="grow mx-1">
        <div class="border border-gray-200 dark:border-gray-600 rounded-md space-y-4 p-4 bg-gray-50 dark:bg-gray-700">
            <h3 class="text-xl font-bold">留学地信息</h3>
            <div class="grid grid-cols-[80px_1fr] text-sm space-y-2 items-start">

                <div>球队名称</div>
                <div>{teamsData[selectedAbroad.id - 255]}</div>

                <div>获得方法</div>
                <div>{currentCondType}</div>

                <div>获得条件</div>
                <div class="flex space-x-2">
                    {#each currentCondValue as item}
                        <span>{item}</span>
                    {/each}
                </div>

                <div>留学时间</div>
                <div>{currentBestTime}</div>

                <div>成长加成</div>
                <VStack>
                    <span>半年： {selectedAbroad.abrUprate[0]}</span>
                    <span>一年： {selectedAbroad.abrUprate[1]}</span>
                    <span>两年： {selectedAbroad.abrUprate[2]}</span>
                </VStack>

                <div>留学效果</div>
                <div>{currentGrowType}</div>

                <div>成长加成</div>
                <VStack>
                    <span>实能力： {selectedAbroad.abrUprate[3]}</span>
                    <span>界限： {selectedAbroad.abrUprate[4]}</span>
                </VStack>

                <div>成长加成</div>
                <VStack>
                    <span>第一次留学： 10</span>
                    <span>第二次留学： 4</span>
                    <span>第三次留学： 1</span>
                </VStack>
            </div>
        </div>
    </VStack>
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

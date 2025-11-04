<script lang="ts">
    import type { Abroad } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import teamsData from "$locales/teams_zh.json";
    import condType from "$locales/cond_type_zh.json";
    import townType from "$locales/town_type_zh.json";
    import sponsors from "$locales/sponsor_zh.json";
    import { getRefreshFlag, getSelectedTab, setIsLoading, setRefreshFlag } from "$lib/globalState.svelte";
    import { sortedAbilities } from "$lib/utils";
    import AbrAbilityBar from "./AbrAbilityBar.svelte";
    import Check from "$lib/icons/Check.svelte";
    import campThemeSame from "$locales/camp_theme_same.json";
    import campThemeDiff from "$locales/camp_theme_diff.json";

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
                return cond.cond.map((i) => sponsors[Number(i)]);
            } else if (cond.id === 7) {
                return cond.cond.map((i) => townType[Number(i)]);
            } else {
                return cond.cond;
            }
        }
        return [];
    });
    let abilityPairs = $derived.by(() => {
        return sortedAbilities.map((label, i) => ({
            label,
            value: selectedAbroad.abrUp[i]
        }));
    });
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
            return selectedType === 0 ? getAbrGrowType([abrUprate[3], abrUprate[4]]) : getCampGrowType(abrUprate[0]);
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

    function getAbrGrowType(input: [number, number]): string {
        if (input[0] >= 90) {
            return "实能";
        } else if (input[1] >= 90) {
            return "界限";
        } else {
            return "平均";
        }
    }

    function getCampGrowType(input: number): string {
        if (input >= 40) {
            return "界限";
        } else {
            return "实能";
        }
    }

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Abroad") {
            try {
                fetchAbroads();
            } finally {
                setRefreshFlag(false);
            }
        }
    });

    const bestTimeZh = ["短期", "标准", "长期"];
    const fixedTimeZh = ["半年限定", "一年限定", "两年限定"];

    function divide100(num: number): string {
        const result = num / 100;
        return result.toFixed(1);
    }

    let themes = ["攻击力强化", "守备力强化", "战术理解强化", "阵型理解强化", "身体强化", "连携强化"];
    let selected: string[] = $state([]);
    let stats = $derived.by(() => {
        if (selected.length == 2) {
            const selected1 = themes.indexOf(selected[0]);
            const selected2 = themes.indexOf(selected[1]);
            if (selected1 === selected2) {
                return campThemeSame[selected1];
            } else {
                return campThemeDiff[selected1].map((element, index) => {
                    return element + campThemeDiff[selected2][index];
                });
            }
        }
        return Array(64).fill(0);
    });

    let campThemeAbilityPairs = $derived.by(() => {
        return sortedAbilities.map((label, i) => ({
            label,
            value: stats[i]
        }));
    });

    function addItem(item: string) {
        if (selected.length >= 2) {
            selected = [...selected.slice(1), item];
        } else {
            selected = [...selected, item];
        }
    }
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
                    {#if selectedType === 0}
                        <AbrAbilityBar value={value} />
                    {:else}
                        <AbrAbilityBar value={value} min={0} max={15} rulerPos={10} />
                    {/if}
                {/if}
            </HStack>
        {/each}
    </VStack>

    <VStack className="grow mx-1">
        <div class="border border-gray-200 dark:border-gray-600 rounded-md space-y-4 p-4 bg-gray-50 dark:bg-gray-700">
            <h3 class="text-xl font-bold">{selectedType === 0 ? "留学地" : "集训地"}信息</h3>
            <div class="grid grid-cols-[80px_1fr] text-sm space-y-4 items-start">

                <div class="text-sm font-medium">球队名称</div>
                <div>{teamsData[selectedAbroad.id - 255]}</div>

                <div class="text-sm font-medium">获得方法</div>
                <div>{currentCondType}</div>

                <div class="text-sm font-medium">获得条件</div>
                <div class="">
                    {#each currentCondValue as item}
                        <div>{item}</div>
                    {/each}
                </div>

                {#if selectedType === 0}
                    <div class="text-sm font-medium">留学时间</div>
                    <div>{currentBestTime}</div>

                    <div class="text-sm font-medium">成长加成</div>
                    <VStack>
                        <span>半年： {divide100(selectedAbroad.abrUprate[0])}</span>
                        <span>一年： {divide100(selectedAbroad.abrUprate[1])}</span>
                        <span>两年： {divide100(selectedAbroad.abrUprate[2])}</span>
                    </VStack>
                {/if}

                <div class="text-sm font-medium">{ selectedType === 0 ? "留学" : "集训" }效果</div>
                <div>{currentGrowType}</div>

                <div class="text-sm font-medium">成长加成</div>
                <VStack>
                    <span>实能力： {selectedType === 0 ? divide100(selectedAbroad.abrUprate[3]) : divide100(selectedAbroad.abrUprate[1])}</span>
                    <span>界限： {selectedType === 0 ? divide100(selectedAbroad.abrUprate[4]) : divide100(selectedAbroad.abrUprate[0])}</span>
                    {#if selectedType === 1}
                        <span>连携： {divide100(selectedAbroad.abrUprate[2])}</span>
                    {/if}
                </VStack>

                {#if selectedType === 0}
                    <div class="text-sm font-medium">成长加成</div>
                    <VStack>
                        <span>第一次留学： 1.0</span>
                        <span>第二次留学： 0.4</span>
                        <span>第三次留学： 0.1</span>
                    </VStack>
                {/if}
            </div>
        </div>

        {#if selectedType !== 0}
            <div class="border border-gray-200 dark:border-gray-600 rounded-lg p-6 bg-gray-50 dark:bg-gray-700 shadow-sm mt-4">
                <h3 class="text-xl font-bold mb-4">集训主题</h3>

                <div class="flex gap-6">
                    <div class="flex flex-col space-y-3 w-32">
                        {#each themes as btn}
                            <button onclick={() => addItem(btn)} class="badges transition">
                                {btn}
                            </button>
                        {/each}
                    </div>

                    <div>
                        <h2 class="text-lg font-semibold mb-3">已选择</h2>
                        {#each selected as item}
                            <div class="text-sm">
                                {item}
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
        {/if}

    </VStack>

    {#if selectedType !== 0}
        <VStack className="w-1/4 h-full overflow-auto mx-2 pl-1">
            {#each campThemeAbilityPairs as { label, value }}
                <HStack className="items-center">
                    <span class="w-24 text-sm">{label}</span>
                    {#if value != null}
                        <AbrAbilityBar value={value} />
                    {/if}
                </HStack>
            {/each}
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

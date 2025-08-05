<script lang="ts">
    import type { BPlayer, MyTeamPlayer } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import RadarChart from "./RadarChart.svelte";
    import StatusBars from "./StatusBars.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import { getCooperationType, getGrowType, getPlayerColor, getPosition, getRank, getRegion, getStyle, getToneType, getFoot, sortedAbilities } from "$lib/utils";
    import { setIsLoading, setModeState } from "$lib/globalState.svelte";
    import AbilityBar from "./AbilityBar.svelte";
    import Football from "$lib/icons/Football.svelte";
    import abilEval from "$locales/abil_eval_zh.json";
    import Comment from "$lib/icons/Comment.svelte";
    import Skull from "$lib/icons/Skull.svelte";
    import Waveform from "./Waveform.svelte";
    import PositionGrid from "./PositionGrid.svelte";
    import About from "./About.svelte";
    import Back from "$lib/icons/Back.svelte";
    import Avatar from "$lib/icons/Avatar.svelte";

    let page = $state(1);
    let total = $state(1);
    let bPlayers: MyTeamPlayer[] = $derived([]);
    let keyword = $state("");

    let selectedPlayer = $state(0);
    let bPlayer: BPlayer = $state({hexagon: [], odc: [], abilities: []});
    let stats = $state(Array(6).fill(0));
    let bars = $state([0, 0, 0]);
    let selectedYear = $state(1);

    let abilityPairs = $derived(
        sortedAbilities.map((label, i) => ({
            label,
            value: [0, 0, bPlayer.abilities[i]]
        }))
    );

    async function fetchBPlayer() {
        if (window.pywebview?.api?.get_bplayer) {
            bPlayer = await window.pywebview.api.get_bplayer(selectedPlayer, selectedYear);
            stats = bPlayer.hexagon;
            bars = [bPlayer.odc[0], bPlayer.odc[1], 0];
        } else {
            alert('API 未加载');
        }
    }

    async function fetchBPlayers() {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_bplayers) {
                const searchParams = keyword ? { "keyword": keyword } : undefined;
                const resp = await window.pywebview.api.fetch_bplayers(page, searchParams);
                page = resp["page"];
                total = resp["total"];
                bPlayers = resp["data"];
                if (bPlayers && bPlayers.length > 0) {
                    selectedPlayer = bPlayers[0].id;
                    await fetchBPlayer();
                } else {
                    selectedPlayer = 0;
                    bPlayers = [];
                    stats = Array(6).fill(0);
                    bars = [0, 0, 0];
                }
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    onMount(async () => {
        fetchBPlayers();
	});

    async function reset() {
        setModeState("");
    }

    async function nextPage() {
        if (page < total) {
            page++;
            fetchBPlayers();
        }
    }

    async function prevPage() {
        if (page > 1) {
            page--;
            fetchBPlayers();
        }
    }

    async function playerClick(id: number) {
        selectedPlayer = id;
        await fetchBPlayer();
    }

    async function nextYear() {
        if (selectedYear < 100) {
            selectedYear++;
            fetchBPlayer();
        }
    }

    async function prevYear() {
        if (selectedYear > 1) {
            selectedYear--;
            fetchBPlayer();
        }
    }

</script>

<VStack className="px-2 flex-1 h-screen">
    <HStack className="items-center w-full py-4">
        <button type="button" onclick={reset} class="pl-2 cursor-pointer mr-auto">
            <Back />
            <span class="sr-only">Back</span>
        </button>

        <nav class="flex items-center gap-x-1">
            <input
                type="text"
                placeholder="球员姓名或id，如：0F8D"
                bind:value={keyword}
                onkeydown={(e) => {
                    if (e.key === 'Enter') {
                        page = 1;
                        fetchBPlayers();
                    }
                }}
                class="w-72 px-4 py-1 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
            />
            <button
                onclick={() => {
                    page = 1;
                    fetchBPlayers();
                }}
                class="flex items-center ml-2 cursor-pointer justify-center border border-gray-200 text-gray-800 py-1 px-3 text-sm rounded-lg dark:border-neutral-700 dark:text-white">
                搜索
            </button>
        </nav>

        <nav class="flex items-center gap-x-1 ml-8">
            <span class="min-h-8 min-w-8 flex justify-center items-center text-gray-800 py-1 px-3 text-sm rounded-lg focus:outline-hidden focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:border-neutral-700 dark:text-white dark:focus:bg-neutral-800">
                年份：
            </span>
            <input type="range" min="1" max="100" bind:value={ selectedYear } class="range">
            <button onclick={fetchBPlayer} class="flex items-center ml-2 cursor-pointer justify-center border border-gray-200 text-gray-800 py-1 px-3 text-sm rounded-lg dark:border-neutral-700 dark:text-white">
                Go
            </button>
            <button onclick={prevYear} type="button" class="min-h-8 min-w-8 py-2 px-2 inline-flex justify-center items-center gap-x-2 text-sm rounded-lg text-gray-800 hover:bg-gray-100 focus:outline-hidden focus:bg-gray-100 disabled:opacity-50 disabled:pointer-events-none dark:text-white dark:hover:bg-white/10 dark:focus:bg-white/10 cursor-pointer" aria-label="Previous">
                <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m15 18-6-6 6-6"></path>
                </svg>
                <span class="sr-only">Previous</span>
            </button>
            <div class="flex items-center gap-x-1">
                <span class="min-h-8 w-12 flex justify-center items-center border border-gray-200 text-gray-800 py-1 px-3 text-sm rounded-lg focus:outline-hidden focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:border-neutral-700 dark:text-white dark:focus:bg-neutral-800">
                    {selectedYear}
                </span>
            </div>
            <button onclick={nextYear} type="button" class="min-h-8 min-w-8 py-2 px-2 inline-flex justify-center items-center gap-x-2 text-sm rounded-lg text-gray-800 hover:bg-gray-100 focus:outline-hidden focus:bg-gray-100 disabled:opacity-50 disabled:pointer-events-none dark:text-white dark:hover:bg-white/10 dark:focus:bg-white/10 cursor-pointer" aria-label="Next">
                <span class="sr-only">Next</span>
                <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m9 18 6-6-6-6"></path>
                </svg>
            </button>
        </nav>

        <About />

    </HStack>
    <HStack className="flex-1 overflow-hidden m-2.5">
        <VStack className="w-1/5 mr-1 space-y-2">
            {#if bPlayers && bPlayers.length > 0}
                <div class="sidebar">
                    {#each bPlayers as item}
                        <button
                            onclick={() => playerClick(item.id)}
                            class={selectedPlayer === item.id ? "activate" : ""}
                            style={`background-image: linear-gradient(to right, transparent 66%, ${getPlayerColor(item.pos)} 100%)`}
                        >
                            <span class="flex items-center justify-between w-full">
                                <HStack className="items-center">
                                    <span>{item.name}</span>
                                    {#if item.scouts && item.scouts.length > 0}
                                        {@const tooltipText = `${item.scouts.join("<br>")}`}
                                        <div class="ml-4">
                                            <Tooltip text={tooltipText} width="80px">
                                                <Avatar />
                                            </Tooltip>
                                        </div>
                                    {/if}
                                </HStack>
                                {#if item.isAlbum}
                                    <div class="mx-2"><Football /></div>
                                {/if}
                            </span>
                        </button>
                    {/each}
                </div>
                <!-- Pagination -->
                <nav class="flex items-center gap-x-1 ml-auto" aria-label="Pagination">
                    <button onclick={prevPage} type="button" class="min-h-8 min-w-8 py-2 px-2 inline-flex justify-center items-center gap-x-2 text-sm rounded-lg text-gray-800 hover:bg-gray-100 focus:outline-hidden focus:bg-gray-100 disabled:opacity-50 disabled:pointer-events-none dark:text-white dark:hover:bg-white/10 dark:focus:bg-white/10 cursor-pointer" aria-label="Previous">
                        <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="m15 18-6-6 6-6"></path>
                        </svg>
                        <span class="sr-only">Previous</span>
                    </button>
                    <div class="flex items-center gap-x-1">
                        <span class="min-h-8 min-w-8 flex justify-center items-center border border-gray-200 text-gray-800 py-1 px-3 text-sm rounded-lg focus:outline-hidden focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:border-neutral-700 dark:text-white dark:focus:bg-neutral-800">
                            {page}
                        </span>
                        <span class="min-h-8 flex justify-center items-center text-gray-500 py-1.5 px-1.5 text-sm dark:text-neutral-500">
                            of
                        </span>
                        <span class="min-h-8 flex justify-center items-center text-gray-500 py-1.5 px-1.5 text-sm dark:text-neutral-500">
                            {total}
                        </span>
                    </div>
                    <button onclick={nextPage} type="button" class="min-h-8 min-w-8 py-2 px-2 inline-flex justify-center items-center gap-x-2 text-sm rounded-lg text-gray-800 hover:bg-gray-100 focus:outline-hidden focus:bg-gray-100 disabled:opacity-50 disabled:pointer-events-none dark:text-white dark:hover:bg-white/10 dark:focus:bg-white/10 cursor-pointer" aria-label="Next">
                        <span class="sr-only">Next</span>
                        <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="m9 18 6-6-6-6"></path>
                        </svg>
                    </button>
                </nav>
                <!-- End Pagination -->
            {:else}
                <div class="border text-sm border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
                    空空如也
                </div>
            {/if}
        </VStack>
        <VStack className="w-1/5 mx-1">
            <div class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
                <p class="flex items-center justify-between">
                    姓名
                    <span class="flex-1 pl-8 text-sm">{bPlayer?.name}</span>
                    {#if bPlayer?.spComment}
                        {@const tooltipText = `${bPlayer.spComment}`}
                        <Tooltip text={tooltipText} width="250px">
                            <Comment />
                        </Tooltip>
                    {/if}
                </p>
                <p>
                    位置
                    <span class="pl-8 text-sm">{getPosition(bPlayer?.pos)}</span>
                </p>
                <p>
                    基础年龄
                    <span class="pl-8 text-sm">{bPlayer?.age}</span>
                </p>
                <p>
                    出生地
                    <span class="pl-8 text-sm">{getRegion(bPlayer?.born)}</span>
                </p>
                <p>
                    惯用脚
                    <span class="pl-8 text-sm">{getFoot(bPlayer?.foot)}</span>
                </p>
                <p>
                    身高
                    <span class="pl-8 text-sm">{bPlayer?.height}</span>
                </p>
                <p>
                    风格
                    <span class="pl-8 text-sm">{getStyle(bPlayer?.style)}</span>
                </p>
                <p>
                    对战评价
                    <span class="pl-8 text-sm">{getRank(bPlayer?.rank)}</span>
                </p>
                <p>
                    出现年份
                    <span class="pl-8 text-sm">{bPlayer?.debutYear}</span>
                </p>
                <p>
                    签约所需声望
                    <span class="pl-8 text-sm">{bPlayer?.signingDifficulty}</span>
                </p>
                <p class="flex items-center justify-between">
                    连携
                    <span  class="flex-1 pl-8 text-sm">{getCooperationType(bPlayer?.cooperationType)}</span>
                    {#if bPlayer?.baddenPlayers}
                        {@const tooltipText = `连携崩坏：<br>${bPlayer.baddenPlayers.join("<br>")}`}
                        <Tooltip text={tooltipText} width="100px">
                            <Skull />
                        </Tooltip>
                    {/if}
                </p>
                <p>
                    性格
                    <span class="pl-8 text-sm">{getToneType(bPlayer?.toneType)}</span>
                </p>
                <p>成长类型</p>
                <div class="pl-4 grid grid-cols-3 gap-x-2 text-sm text-left">
                    <div>身体</div>
                    <div>技术</div>
                    <div>头脑</div>
                    <div>{getGrowType(bPlayer?.growTypePhy)}</div>
                    <div>{getGrowType(bPlayer?.growTypeTec)}</div>
                    <div>{getGrowType(bPlayer?.growTypeSys)}</div>
                </div>
                <p>隐藏属性</p>
                <div class="pl-4 grid grid-cols-2 gap-x-1 text-sm text-left">
                    <div><span>人气</span><span class="pl-3">{bPlayer?.pop}</span></div>
                    <div><span>欲望</span><span class="pl-3">{bPlayer?.desire}</span></div>
                    <div><span>自尊</span><span class="pl-3">{bPlayer?.pride}</span></div>
                    <div><span>野心</span><span class="pl-3">{bPlayer?.ambition}</span></div>
                    <div><span>毅力</span><span class="pl-3">{bPlayer?.persistence}</span></div>
                    <div><span>耐心</span><span class="pl-3">{bPlayer?.patient}</span></div>
                    <div><span>超级替补</span><span class="pl-3">{bPlayer?.superSub}</span></div>
                    <div><span>公平竞赛</span><span class="pl-3">{bPlayer?.wildType}</span></div>
                    <div><span>受伤耐性</span><span class="pl-3">{bPlayer?.weakType}</span></div>
                    <div><span>疲劳耐性</span><span class="pl-3">{bPlayer?.tiredType}</span></div>
                    <div><span>波动指数</span><span class="pl-3">{bPlayer?.waveType}</span></div>
                </div>
            </div>
        </VStack>
        <VStack className="w-3/10 mx-1">
            {#if bPlayer?.abilEval}
                <Tooltip text={abilEval[bPlayer.abilEval]} width="220px">
                    <RadarChart abilities={stats} />
                </Tooltip>
            {/if}
            <HStack className="w-full grid grid-cols-2">
                <StatusBars values={bars} pos={bPlayer.pos} />
                <PositionGrid aposEval={bPlayer.aposEval} />
            </HStack>
            <Waveform phyGrows={bPlayer?.phyGrows} tecGrows={bPlayer?.tecGrows} sysGrows={bPlayer?.sysGrows} />
            {#if bPlayer?.abilEval}
                <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
                    <p>{abilEval[bPlayer.abilEval]}</p>
                </div>
            {/if}
        </VStack>

        <VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
            {#each abilityPairs as { label, value }}
                <HStack className="items-center">
                    <span class="w-24 text-sm">{label}</span>
                    {#if value}
                        {@const tooltipText = `上限: ${value[2]}`}
                        <Tooltip text={tooltipText} className="w-full">
                            <AbilityBar abilities={value} />
                        </Tooltip>
                    {/if}
                </HStack>
            {/each}
        </VStack>
    </HStack>
</VStack>

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
    .range {
        @apply w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700;
    }
</style>

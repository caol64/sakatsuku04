<script lang="ts">
    import type { Coach } from "$lib/models";
    import { onMount } from "svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import { setIsLoading, setModeState } from "$lib/globalState.svelte";
    import About from "./About.svelte";
    import Back from "$lib/icons/Back.svelte";
    import BCoachDetails from "./BCoachDetails.svelte";
    import Airplane from "$lib/icons/Airplane.svelte";
    import Component from "$lib/icons/Component.svelte";

    let page = $state(1);
    let total = $state(1);
    let bCoachs: Coach[] = $derived([]);
    let keyword = $state("");
    let selectedCoach = $state(0);
    let inputPage = $derived(page.toString());

    async function fetchBCoachs() {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_bcoachs) {
                const searchParams = keyword ? { "keyword": keyword } : undefined;
                const resp = await window.pywebview.api.fetch_bcoachs(page, searchParams);
                page = resp["page"];
                total = resp["total"];
                bCoachs = resp["data"];
                if (bCoachs && bCoachs.length > 0) {
                    selectedCoach = bCoachs[0].id;
                } else {
                    selectedCoach = 0;
                    bCoachs = [];
                }
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    onMount(async () => {
        fetchBCoachs();
	});

    async function reset() {
        setModeState("");
    }

    async function nextPage() {
        if (page < total) {
            page++;
            fetchBCoachs();
        }
    }

    async function prevPage() {
        if (page > 1) {
            page--;
            fetchBCoachs();
        }
    }

    async function scoutClick(id: number) {
        selectedCoach = id;
    }

    function onJumpPage() {
        let targetPage = parseInt(inputPage);
        if (!isNaN(targetPage) && targetPage >= 1 && targetPage <= total) {
            page = targetPage;
            fetchBCoachs();
        } else {
            inputPage = page.toString();
        }
    }

</script>

<VStack className="px-2 flex-1 h-screen">
    <HStack className="items-center w-full h-13">
        <button type="button" onclick={reset} class="pl-2 cursor-pointer mr-auto">
            <Back />
            <span class="sr-only">Back</span>
        </button>

        <nav class="flex items-center gap-x-1">
            <input
                type="text"
                placeholder="教练姓名或id，如：0F8D"
                bind:value={keyword}
                onkeydown={(e) => {
                    if (e.key === 'Enter') {
                        page = 1;
                        fetchBCoachs();
                    }
                }}
                class="w-72 px-4 py-1 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
            />
            <button
                onclick={() => {
                    page = 1;
                    fetchBCoachs();
                }}
                class="flex items-center ml-2 cursor-pointer justify-center border border-gray-200 text-gray-800 py-1 px-3 text-sm rounded-lg dark:border-neutral-700 dark:text-white">
                搜索
            </button>
        </nav>

        <About />

    </HStack>
    <HStack className="flex-1 overflow-hidden m-2.5">
        <VStack className="w-1/5 mr-1 space-y-2">
            {#if bCoachs && bCoachs.length > 0}
                <div class="sidebar">
                    {#each bCoachs as item}
                        <button
                            onclick={() => scoutClick(item.id)}
                            class={selectedCoach === item.id ? "activate" : ""}
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
                <!-- Pagination -->
                <nav class="flex items-center gap-x-1 ml-auto" aria-label="Pagination">
                    <button onclick={prevPage} type="button" class="min-h-8 min-w-8 py-2 px-2 inline-flex justify-center items-center gap-x-2 text-sm rounded-lg text-gray-800 hover:bg-gray-100 focus:outline-hidden focus:bg-gray-100 disabled:opacity-50 disabled:pointer-events-none dark:text-white dark:hover:bg-white/10 dark:focus:bg-white/10 cursor-pointer" aria-label="Previous">
                        <svg class="shrink-0 size-3.5" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="m15 18-6-6 6-6"></path>
                        </svg>
                        <span class="sr-only">Previous</span>
                    </button>
                    <div class="flex items-center gap-x-1">
                        <input type="text" bind:value={inputPage}
                            onkeydown={(e) => {
                                if (e.key === 'Enter') {
                                    onJumpPage();
                                }
                            }}
                            class="min-h-8 w-12 flex justify-center items-center border border-gray-200 text-gray-800 py-1 px-3 text-sm rounded-lg focus:outline-hidden focus:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none dark:border-neutral-700 dark:text-white dark:focus:bg-neutral-800" />
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

        <BCoachDetails selectedCoach={selectedCoach} />
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
</style>

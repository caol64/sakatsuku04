<script lang="ts">
    import { allTabs, setIsLoading, getSelectedTab, setSelectedTab, setDefaultTab, type Tab, getSaveList, setClubData, setModeState, setSaveList, getClubData, getModeState, setRefreshFlag } from "$lib/globalState.svelte";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import Back from "$lib/icons/Back.svelte";
    import { onMount } from "svelte";
    import Refresh from "$lib/icons/Refresh.svelte";
    import About from "./About.svelte";
    import DropDown from "$lib/icons/DropDown.svelte";

    let selectedGame = $state("");

    async function changeTab(name: Tab) {
        if (getSelectedTab() !== name) {
            setSelectedTab(name);
        }
    }

    async function selectGame() {
        try {
            setIsLoading(true);
            setDefaultTab();
            if (window.pywebview?.api?.select_game) {
                await window.pywebview.api.select_game(selectedGame);
                const pageData = await window.pywebview.api.fetch_club_data();
                if (pageData) {
                    setClubData(pageData);
                }
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }

    }

    async function reset() {
        setModeState("");
        setSaveList([]);
        setClubData({});
        setDefaultTab();
        selectedGame = "";
    }

    async function refresh() {
        if (getSelectedTab() === "Game") {
            selectGame();
        } else {
            setRefreshFlag(true);
        }
    }

    onMount(() => {
        if (getSaveList()) {
            selectedGame = getSaveList()[0];
        }
        selectGame();
    });
</script>

<HStack className="items-center w-full">
    <button type="button" onclick={reset} class="cursor-pointer mx-2">
        <Back />
        <span class="sr-only">Back</span>
    </button>

    <ul class="flex-1 flex space-x-4 mx-2">
        {#each allTabs as item}
            <li>
                <button onclick={() => changeTab(item)} class={ getSelectedTab() === item ? "activate" : "" }>{ item }</button>
            </li>
        {/each}
    </ul>

    {#if getSaveList().length > 0}
        <div class="mx-auto">
            <div class="relative">
                <select bind:value={selectedGame} onchange={selectGame} class="w-full bg-transparent placeholder:text-slate-400 text-slate-700 dark:text-gray-300 text-sm border border-slate-200 rounded pl-3 pr-8 py-2 transition duration-300 focus:outline-none focus:border-slate-400 hover:border-slate-400 shadow-sm focus:shadow-md appearance-none cursor-pointer">
                    {#each getSaveList() as item}
                        <option>{ item }</option>
                    {/each}
                </select>
                <DropDown />
            </div>
        </div>
    {/if}

    {#if getModeState() === "memoryEditor"}
        <button onclick={refresh} class="cursor-pointer ml-2">
            <Refresh />
            <span class="sr-only">Refresh</span>
        </button>
    {/if}

    <About />

</HStack>

<style lang="postcss">
    @reference "tailwindcss";
    ul {
        @apply flex flex-wrap text-sm font-medium text-center text-gray-500 border-b border-gray-200 dark:border-gray-700 dark:text-gray-400;
    }
    li button {
        @apply inline-block p-4 rounded-t-lg cursor-pointer hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-gray-300;
    }
    li {
        @apply me-2;
    }
    .activate {
        @apply text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-300;
    }
</style>

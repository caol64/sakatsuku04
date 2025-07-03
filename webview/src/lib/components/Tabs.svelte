<script lang="ts">
    import { allTabs, getSelectedTab, setSelectedTab, type Tab, getSaveList, setClubData, setModeState, setSaveList, getClubData, getModeState } from "$lib/globalState.svelte";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import Back from "$lib/icons/Back.svelte";
    import { onMount } from "svelte";
    import { defaultClubData } from "$lib/models";
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
        setSelectedTab("Club");
        if (window.pywebview?.api?.select_game) {
            await window.pywebview.api.select_game(selectedGame);
            const pageData = await window.pywebview.api.fetch_club_data();
            if (pageData) {
                setClubData(pageData);
            }
        } else {
            alert('pywebview API 未加载');
        }
    }

    async function reset() {
        setModeState("");
        setSaveList([]);
        setClubData(defaultClubData);
        setSelectedTab("Club");
        selectedGame = "";
    }

    onMount(() => {
        if (getSaveList()) {
            selectedGame = getSaveList()[0];
        }
        selectGame();
    });

    async function handleSave() {
        if (window.pywebview?.api?.save_club_data) {
            console.log(getClubData());
            // const pageData: Response = await window.pywebview.api.save_club_data(getBaseData(), selectedGame);
            // if (pageData) {
            //     console.log(pageData);
            // }
        } else {
            alert('pywebview API 未加载');
        }
    }
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
        <button class="cursor-pointer ml-2">
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

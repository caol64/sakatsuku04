<script lang="ts">
    import { allTabs, getSelectedTab, setSelectedTab, type Tab, getSaveList, setBaseData, setModeState, setSaveList, getBaseData } from "$lib/globalState.svelte";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import More from "$lib/icons/More.svelte";
    import Back from "$lib/icons/Back.svelte";
    import { onMount } from "svelte";
    import { defaultBaseData } from "$lib/models";

    let selectedGame = $state("");

    async function changeTab(name: Tab) {
        if (getSelectedTab() !== name) {
            setSelectedTab(name);
        }
    }

    async function fetchSaveData() {
        setSelectedTab("Base");
        if (window.pywebview?.api?.fetch_save_data) {
            const pageData = await window.pywebview.api.fetch_save_data(selectedGame);
            if (pageData) {
                setBaseData(pageData);
            }
        } else {
            alert('pywebview API 未加载');
        }
    }

    async function reset() {
        if (window.pywebview?.api?.reset) {
            await window.pywebview.api.reset();
        } else {
            alert('pywebview API 未加载');
        }
        setModeState("");
        setSaveList([]);
        setBaseData(defaultBaseData);
        setSelectedTab("Base");
        selectedGame = "";
    }

    onMount(() => {
        if (getSaveList()) {
            selectedGame = getSaveList()[0].name;
            fetchSaveData();
        }
    });

    async function handleSave() {
        if (window.pywebview?.api?.save_club_data) {
            console.log(getBaseData());
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

    <div class="mx-auto">
        <div class="relative">
            <select bind:value={selectedGame} onchange={fetchSaveData} class="w-full bg-transparent placeholder:text-slate-400 text-slate-700 text-sm border border-slate-200 rounded pl-3 pr-8 py-2 transition duration-300 ease focus:outline-none focus:border-slate-400 hover:border-slate-400 shadow-sm focus:shadow-md appearance-none cursor-pointer">
                {#each getSaveList() as item}
                    <option>{ item.name }</option>
                {/each}
            </select>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.2" stroke="currentColor" class="h-5 w-5 ml-1 absolute top-2.5 right-2.5 text-slate-700">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15 12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
            </svg>
        </div>
    </div>

    <button onclick={handleSave} class="w-18 h-8 rounded-md cursor-pointer mx-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
        保存
    </button>

    <button class="cursor-pointer mr-2">
        <More />
        <span class="sr-only">More</span>
    </button>

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

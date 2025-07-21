<script lang="ts">
    import { getRefreshFlag, getSelectedTab, setIsLoading, setRefreshFlag } from "$lib/globalState.svelte";
    import type { MyTown } from "$lib/models";
    import { onMount } from "svelte";

    let myTown: MyTown = $state({});

    async function fetchMyTown() {
        try {
            setIsLoading(true);
            if (window.pywebview?.api?.fetch_my_town) {
                myTown = await window.pywebview.api.fetch_my_town();
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    onMount(async () => {
        fetchMyTown();
	});

    async function handleSave() {
        if (window.pywebview?.api?.save_my_town) {
            const { message } = await window.pywebview.api.save_my_town(myTown);
            if (message === "success") {
                alert("修改成功");
                fetchMyTown();
            } else {
                alert(message);
            }
        } else {
            alert('API 未加载');
        }
    }

    $effect(() => {
        if(getRefreshFlag() && getSelectedTab() === "Town") {
            try {
                fetchMyTown();
            } finally {
                setRefreshFlag(false);
            }
        }
    });

</script>

<div class="bg-gray-50 dark:bg-gray-700 rounded-2xl shadow p-6 flex flex-col space-y-8 m-8">
    <h2 class="text-xl font-bold">城市信息</h2>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">人口</span>
        <span>{myTown.population}</span>
        <input type="range" min="1" max="9999999" bind:value={ myTown.population } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">地价</span>
        <span>{myTown.price}</span>
        <input type="range" min="1" max="100" bind:value={ myTown.price } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">交通</span>
        <span>{myTown.trafficLevel}</span>
        <input type="range" min="1" max="100" bind:value={ myTown.trafficLevel } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">足球人气</span>
        <span>{myTown.soccerPop}</span>
        <input type="range" min="1" max="100" bind:value={ myTown.soccerPop } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">足球水平</span>
        <span>{myTown.soccerLevel}</span>
        <input type="range" min="1" max="65535" bind:value={ myTown.soccerLevel } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">住宅</span>
        <span>{myTown.living}</span>
        <input type="range" min="1" max="65535" bind:value={ myTown.living } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">经济</span>
        <span>{myTown.economy}</span>
        <input type="range" min="1" max="65535" bind:value={ myTown.economy } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">体育</span>
        <span>{myTown.sports}</span>
        <input type="range" min="1" max="65535" bind:value={ myTown.sports } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
    <div class="grid grid-cols-3 items-center w-fit">
        <span class="label">环境</span>
        <span>{myTown.env}</span>
        <input type="range" min="1" max="65535" bind:value={ myTown.env } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
    </div>
</div>

<div class="flex justify-center">
    <button onclick={handleSave} class="w-18 h-8 rounded-md cursor-pointer text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
        保存
    </button>
</div>

<style lang="postcss">
    @reference "tailwindcss";
    .label {
        @apply block text-sm font-medium text-gray-900 dark:text-white;
    }
</style>

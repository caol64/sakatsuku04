<script lang="ts">
    import { getClubData } from "$lib/globalState.svelte";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import { defaultClubData } from "$lib/models";

    const pattern = "^([1-9][0-9]{0,3}|0)$";
    let clubData = $state(defaultClubData);

    $effect(() => {
        clubData = getClubData();
    });
</script>

<VStack className="m-2.5">
    <div class="mb-6 mt-3">
        <label for="clubname">球会名</label>
        <input id="clubname" bind:value={ clubData.clubName } class="input" required />
    </div>
    <div class="mb-6">
        <label for="fundsHigh">资金</label>
        <HStack className="gap-4">
            <div class="relative">
                <input type="text" id="fundsHigh" maxlength="4" pattern={pattern} title="请输入 0 到 9999 之间的整数" bind:value={ clubData.fundsHigh } class="input" required />
                <div class="inner">
                    <span>亿</span>
                </div>
            </div>
            <div class="relative">
                <input type="text" id="fundsLow" maxlength="4" pattern={pattern} title="请输入 0 到 9999 之间的整数" bind:value={ clubData.fundsLow } class="input" required />
                <div class="inner">
                    <span>万</span>
                </div>
            </div>
        </HStack>
    </div>
    <div class="mb-6">
        <label for="year">游戏年份</label>
        <HStack className="gap-4">
            <div class="relative">
                <input type="text" id="year" maxlength="4" pattern={pattern} title="请输入 0 到 9999 之间的整数" bind:value={ clubData.year } class="input" required />
                <div class="inner">
                    <span>年</span>
                </div>
            </div>
            <div class="relative">
                <input type="text" id="month" maxlength="2" pattern={pattern} title="请输入 1 到 12 之间的整数" bind:value={ clubData.month } class="input" required />
                <div class="inner">
                    <span>月</span>
                </div>
            </div>
            <div class="relative">
                <input type="text" id="date" maxlength="2" pattern={pattern} title="请输入 1 到 31 之间的整数" bind:value={ clubData.date } class="input" required />
                <div class="inner">
                    <span>日</span>
                </div>
            </div>
        </HStack>
    </div>
    <div class="mb-6">
        <label for="managerName">球队经理</label>
        <input id="managerName" bind:value={ clubData.managerName } class="input" required />
    </div>
    <div class="mb-6">
        <label for="gameDifficulty">游戏难度</label>
        <HStack className="items-center">
            <span class="text-sm w-16">{ clubData.difficulty }</span>
            <input id="gameDifficulty" type="range" min="0" max="31" bind:value={ clubData.difficulty } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
        </HStack>
    </div>
    <button class="w-18 h-8 rounded-md cursor-pointer mx-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
        保存
    </button>
</VStack>

<style lang="postcss">
    @reference "tailwindcss";
    label {
        @apply block mb-2 text-sm font-medium text-gray-900 dark:text-white;
    }
    .input {
        @apply bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500;
    }
    .inner {
        @apply absolute inset-y-0 end-0 top-0 flex items-center pe-3.5 pointer-events-none;
    }
</style>

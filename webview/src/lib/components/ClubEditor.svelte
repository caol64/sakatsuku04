<script lang="ts">
    import { getClubData } from "$lib/globalState.svelte";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import type { Club } from "$lib/models";

    const pattern = "^([1-9][0-9]{0,3}|0)$";
    let clubData: Club = $state({});

    $effect(() => {
        clubData = getClubData();
    });

    async function handleSave() {
        if (window.pywebview?.api?.save_club_data) {
            const { message } = await window.pywebview.api.save_club_data(clubData);
            if (message === "success") {
                alert("修改成功");
            } else {
                alert(message);
            }
        } else {
            alert('API 未加载');
        }
    }
</script>

<div class="w-full h-full p-8 grid grid-cols-2 gap-8">
    <div class="bg-gray-50 dark:bg-gray-700 rounded-2xl shadow p-6 flex flex-col space-y-6">
        <h2 class="text-xl font-bold">球队信息</h2>
        <div class="mb-6 mt-3">
            <label for="clubname">球会名</label>
            <input id="clubname" bind:value={ clubData.clubName } class="input" required disabled />
        </div>
        <div class="mb-6">
        <label for="fundsHigh">资金</label>
        <HStack className="gap-4 mb-6">
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
        <div>
            <label for="managerName">球队经理</label>
            <input id="managerName" bind:value={ clubData.managerName } class="input" required disabled />
        </div>
    </div>
    </div>
    <div class="bg-gray-50 dark:bg-gray-700 rounded-2xl shadow p-6 flex flex-col space-y-6">
        <h2 class="text-xl font-bold">游戏设置</h2>
        <div class="mb-6 mt-3">
            <label for="year">游戏年份</label>
            <HStack className="gap-4">
                <div class="relative">
                    <input type="text" id="year" maxlength="4" pattern={pattern} title="请输入 0 到 9999 之间的整数" bind:value={ clubData.year } class="input w-30" required />
                    <div class="inner">
                        <span>年</span>
                    </div>
                </div>
                <div class="relative">
                    <input type="text" id="month" maxlength="2" pattern={pattern} title="请输入 1 到 12 之间的整数" bind:value={ clubData.month } class="input w-30" required disabled />
                    <div class="inner">
                        <span>月</span>
                    </div>
                </div>
                <div class="relative">
                    <input type="text" id="date" maxlength="2" pattern={pattern} title="请输入 1 到 31 之间的整数" bind:value={ clubData.date } class="input w-30" required disabled />
                    <div class="inner">
                        <span>日</span>
                    </div>
                </div>
            </HStack>
        </div>
        <div class="mb-6">
            <label for="gameDifficulty">游戏难度</label>
            <HStack className="items-center mt-3">
                <span class="text-sm w-16">{ clubData.difficulty }</span>
                <input id="gameDifficulty" type="range" min="0" max="31" bind:value={ clubData.difficulty } class="w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-400">
            </HStack>
        </div>
        <div>
            <label for="seed">随机种子</label>
            <input id="seed" bind:value={ clubData.seed } class="input" required disabled />
        </div>
    </div>
    <div class="col-span-2 flex justify-center mt-4">
        <button onclick={handleSave} class="w-18 h-8 rounded-md cursor-pointer text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
            保存
        </button>
    </div>
</div>

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

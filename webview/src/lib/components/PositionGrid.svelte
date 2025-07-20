<script lang="ts">
    let { aposEval = Array(11).fill(0) }: { aposEval?: number[] } = $props();
    // 颜色映射表
    const colorMap = ["bg-white", "bg-cyan-400", "bg-yellow-300", "bg-orange-400", "bg-red-500"];

    // 三列颜色（从下往上）
    let leftCol = $derived([
        colorMap[aposEval[9]],  // 上左
        colorMap[aposEval[5]],  // 中左
        colorMap[aposEval[2]],  // 下左
    ]);

    let middleCol = $derived([
        colorMap[aposEval[8]],  // 中最上
        colorMap[aposEval[7]],  // 中靠上
        colorMap[aposEval[4]],  // 中靠下
        colorMap[aposEval[1]],  // 中最下
    ]);

    let rightCol = $derived([
        colorMap[aposEval[10]],  // 上右
        colorMap[aposEval[6]],  // 中右
        colorMap[aposEval[3]], // 下右
    ]);

    let extraCol = $derived(colorMap[aposEval[0]]);
</script>

<div class="flex flex-col items-center p-2 rounded-lg bg-white dark:bg-gray-700 my-1">
    <div class="text-gray-500 font-bold tracking-wide mb-1">POSITION</div>

    <div class="relative flex flex-col items-center w-[100px]">
        <!-- 三列主图形 -->
        <div class="flex w-full h-[80px] border-2 border-gray-500">
            <!-- 左列 -->
            <div class="flex flex-col w-1/3">
                {#each leftCol as color}
                    <div class="{color} aspect-square border border-slate-800 h-[26.6667px]"></div>
                {/each}
            </div>

            <!-- 中列 -->
            <div class="flex flex-col w-1/3">
                {#each middleCol as color}
                    <div class="{color} flex-1 border border-slate-800"></div>
                {/each}
            </div>

            <!-- 右列 -->
            <div class="flex flex-col w-1/3">
                {#each rightCol as color}
                    <div class="{color} aspect-square border border-slate-800 h-[26.6667px]"></div>
                {/each}
            </div>
        </div>

        <!-- 额外的中间格子：直接位于主图形下方 -->
        <div class="w-1/3 flex-none">
            <div class="{extraCol} flex-1 h-[20px] border-2 border-slate-800"></div>
        </div>
    </div>
</div>

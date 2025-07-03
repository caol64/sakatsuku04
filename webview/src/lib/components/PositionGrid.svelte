<script lang="ts">
    const leftCol = ["bg-orange-600", "bg-red-600", "bg-orange-600"];
    const middleCol = [
        "bg-orange-600",
        "bg-cyan-400",
        "bg-cyan-400",
        "bg-cyan-400",
    ];
    const rightCol = ["bg-cyan-400", "bg-orange-600", "bg-cyan-400"];
</script>

<div class="flex flex-col items-center p-2 rounded-lg bg-white dark:bg-gray-700">
    <div class="text-gray-500 font-bold tracking-wide mb-1">POSITION</div>

    <div class="relative flex flex-col items-center w-[100px]">
        <!-- 三列主图形 -->
        <div class="flex w-full h-[100px] border-2 border-gray-500">
            <!-- 左列 -->
            <div class="flex flex-col w-1/3">
                {#each leftCol as color}
                    <div
                        class="{color} aspect-square border border-slate-800"
                    ></div>
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
                    <div
                        class="{color} aspect-square border border-slate-800"
                    ></div>
                {/each}
            </div>
        </div>

        <!-- 额外的中间格子：直接位于主图形下方 -->
        <div class="w-1/3 flex-none">
            <div
                class="bg-green-500 flex-1 h-[25px] border border-slate-800"
            ></div>
        </div>
    </div>
</div>

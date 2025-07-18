<script lang="ts">
    const width = 800;
    const height = 300;
    const padding = { top: 30, right: 20, bottom: 40, left: 20 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const minAge = 16;
    const maxAge = 40;
    const maxValue = 10;

    let {
        phyGrows = Array(25).fill(0),
        tecGrows = Array(25).fill(0),
        sysGrows = Array(25).fill(0),
        currentAge = 0,
    }: {
        phyGrows?: number[],
        tecGrows?: number[],
        sysGrows?: number[],
        currentAge?: number,
    } = $props();

    const xScale = (age: number): number => ((age - minAge) / (maxAge - minAge)) * chartWidth;
    const yScale = (value: number): number => chartHeight - (value / maxValue) * chartHeight;

    const createSmoothPath = (points: { x: number; y: number }[]): string => {
        if (points.length < 2) return "";
        let path = `M ${points[0].x} ${points[0].y}`;
        for (let i = 0; i < points.length - 1; i++) {
            const p0 = points[i - 1] || points[i];
            const p1 = points[i];
            const p2 = points[i + 1];
            const p3 = points[i + 2] || p2;
            const t = 0.2;
            const cp1x = p1.x + ((p2.x - p0.x) / 6) * t * 2;
            const cp1y = p1.y + ((p2.y - p0.y) / 6) * t * 2;
            const cp2x = p2.x - ((p3.x - p1.x) / 6) * t * 2;
            const cp2y = p2.y - ((p3.y - p1.y) / 6) * t * 2;
            path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
        }
        return path;
    };

    function createData(values: number[]) {
        return values.map((v, i) => {
            const age = i + 16;
            return {
                age,
                value: v,
                x: xScale(age),
                y: yScale(v),
            };
        });
    }

    let phyGrowsData = $derived(createData(phyGrows));
    let tecGrowsData = $derived(createData(tecGrows));
    let sysGrowsData = $derived(createData(sysGrows));

    const pointAt = (data: typeof phyGrowsData, age: number) => data.find((d) => d.age === age);
</script>

<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white py-4 px-2 rounded border border-gray-200 dark:border-gray-700">
    <div class="flex justify-center space-x-4 mb-4 text-sm">
        <div class="flex items-center space-x-2">
            <span class="w-4 h-1 bg-cyan-500 dark:bg-cyan-400 rounded-full"></span>
            <span>身体</span>
        </div>
        <div class="flex items-center space-x-2">
            <span class="w-4 h-1 bg-rose-500 dark:bg-rose-400 rounded-full"></span>
            <span>技术</span>
        </div>
        <div class="flex items-center space-x-2">
            <span class="w-4 h-1 bg-lime-500 dark:bg-lime-400 rounded-full"></span>
            <span>头脑</span>
        </div>
    </div>

    <svg {width} {height} viewBox={`0 0 ${width} ${height}`} class="w-full h-auto">
        <g transform={`translate(${padding.left}, ${padding.top})`}>
            <!-- 坐标轴与网格线 -->
            {#each Array.from({ length: 11 }, (_, i) => i) as tick}
                <g transform="translate(0, {yScale(tick)})">
                    {#if tick == 7}
                        <line x1="0" x2={chartWidth} class="stroke-red-500" stroke-dasharray="4 4" />
                    {/if}
                    <!-- <text x="-10" dy="0.32em" text-anchor="end" class="fill-current text-xs">{tick}</text> -->
                </g>
            {/each}
            {#each [16, 20, 25, 30, 35, 40] as tick}
                <g transform="translate({xScale(tick)}, {chartHeight})">
                    <text y="20" text-anchor="middle" class="fill-current text-3xl">{tick}岁</text>
                </g>
            {/each}
            <line x1="0" y1={chartHeight} x2={chartWidth} y2={chartHeight} class="stroke-current opacity-50" />

            <!-- 曲线 -->
            <path d={createSmoothPath(phyGrowsData)} class="stroke-cyan-500 dark:stroke-cyan-400" fill="none" stroke-width="2" />
            <path d={createSmoothPath(tecGrowsData)} class="stroke-rose-500 dark:stroke-rose-400" fill="none" stroke-width="2" />
            <path d={createSmoothPath(sysGrowsData)} class="stroke-lime-500 dark:stroke-lime-400" fill="none" stroke-width="2" />

            <!-- 当前年龄垂直线 -->
            {#if pointAt(phyGrowsData, currentAge)}
                <line
                    x1={pointAt(phyGrowsData, currentAge)!.x}
                    x2={pointAt(phyGrowsData, currentAge)!.x}
                    y1={yScale(maxValue)}
                    y2={chartHeight}
                    class="stroke-gray-500 dark:stroke-gray-400"
                    stroke-width="2"
                    stroke-dasharray="4 4"
                />
            {/if}

            <!-- 指示器 -->
            <!-- {#each [
                { label: '身体', color: 'cyan', point: pointAt(data1, currentAge) },
                { label: '技术', color: 'rose', point: pointAt(data2, currentAge) },
                { label: '头脑', color: 'lime', point: pointAt(data3, currentAge) },
            ] as item (item.label)}
                {#if item.point}
                    <g>
                        <circle
                            cx={item.point.x}
                            cy={item.point.y}
                            r="6"
                            class={`fill-${item.color}-500 dark:fill-${item.color}-400`}
                        />
                        <circle
                            cx={item.point.x}
                            cy={item.point.y}
                            r="10"
                            class={`fill-${item.color}-500 dark:fill-${item.color}-400 opacity-30`}
                        />
                        <text
                            x={item.point.x}
                            y={item.point.y - 15}
                            text-anchor="middle"
                            class={`fill-${item.color}-500 dark:fill-${item.color}-400 font-bold text-sm`}
                        >
                            {item.point.value.toFixed(0)}
                        </text>
                    </g>
                {/if}
            {/each} -->
        </g>
    </svg>
</div>

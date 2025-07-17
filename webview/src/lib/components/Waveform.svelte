<!-- src/lib/Waveform.svelte -->
<script lang="ts">
    import { tweened } from "svelte/motion";

    interface DataPoint {
        age: number;
        value: number;
    }

    // --- 使用 $state 并指定类型 ---
    let selectedAge = $state<number>(25);

    // --- 为函数添加返回类型 ---
    function generatePlayerData(): DataPoint[] {
        const data: DataPoint[] = [];
        const baseGrowth = 50;
        for (let age = 16; age <= 40; age++) {
            const fluctuation1 = Math.sin((age - 16) * 0.5) * 20;
            const fluctuation2 = Math.sin((age - 16) * 1.5) * 10;
            const randomNoise = (Math.random() - 0.5) * 5;
            let value = baseGrowth + fluctuation1 + fluctuation2 + randomNoise;
            value = Math.max(0, Math.min(100, value));
            data.push({ age, value });
        }
        return data;
    }

    // --- 本地类型定义 ---
    // 扩展 DataPoint 以包含 SVG 坐标
    type ScaledDataPoint = DataPoint & {
        x: number;
        y: number;
    };

    // 指示器动画对象类型
    type IndicatorCoords = {
        x: number;
        y: number;
        value: number;
    };

    // --- Props (使用泛型为 $props 添加类型) ---
    type Props = {
        data: DataPoint[];
        currentAge: number | null;
    };
    let { data = [], currentAge = null } = $props();

    // --- 常量 ---
    const width = 800;
    const height = 300;
    const padding = { top: 30, right: 30, bottom: 40, left: 40 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const minAge = 16;
    const maxAge = 40;
    const maxValue = 100;

    // --- 类型化的函数 ---
    const xScale = (age: number): number =>
        ((age - minAge) / (maxAge - minAge)) * chartWidth;
    const yScale = (value: number): number =>
        chartHeight - (value / maxValue) * chartHeight;

    const createSmoothPath = (points: ScaledDataPoint[]): string => {
        if (points.length < 2) return "";
        let path = `M ${points[0].x} ${points[0].y}`;
        for (let i = 0; i < points.length - 1; i++) {
            const p0 = points[i - 1] || points[i];
            const p1 = points[i];
            const p2 = points[i + 1];
            const p3 = points[i + 2] || p2;
            const tension = 0.2;
            const cp1x = p1.x + ((p2.x - p0.x) / 6) * tension * 2;
            const cp1y = p1.y + ((p2.y - p0.y) / 6) * tension * 2;
            const cp2x = p2.x - ((p3.x - p1.x) / 6) * tension * 2;
            const cp2y = p2.y - ((p3.y - p1.y) / 6) * tension * 2;
            path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
        }
        return path;
    };

    // --- 派生状态 (添加类型) ---
    const scaledPoints = $derived<ScaledDataPoint[]>(
        generatePlayerData().map((d) => ({
            x: xScale(d.age),
            y: yScale(d.value),
            ...d,
        })),
    );

    const pathData = $derived<string>(createSmoothPath(scaledPoints));

    // .find() 可能返回 undefined，所以类型是 ScaledDataPoint | undefined
    const currentPoint = $derived<ScaledDataPoint | undefined>(
        scaledPoints.find((p) => p.age === selectedAge),
    );

    // --- 动画 (添加类型) ---
    const indicatorCoords = tweened<IndicatorCoords>(
        { x: 0, y: 0, value: 0 },
        { duration: 250 },
    );

    $effect(() => {
        // TypeScript 知道这里的 currentPoint 是 ScaledDataPoint 类型，因为有 if 判断
        if (currentPoint) {
            indicatorCoords.set(
                {
                    x: currentPoint.x,
                    y: currentPoint.y,
                    value: currentPoint.value,
                },
                { duration: 150 },
            );
        }
    });
</script>

<!-- Markup 保持不变 -->
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-4 rounded shadow-xl border border-gray-200 dark:border-gray-700">
    <svg {width} {height} class="w-full h-auto" viewBox="0 0 {width} {height}">
        <g transform="translate({padding.left}, {padding.top})">
            <!-- 坐标轴和网格线 -->
            <g class="axes text-xs text-gray-500 dark:text-gray-400">
                {#each [0, 25, 50, 75, 100] as tick}
                    <g transform="translate(0, {yScale(tick)})">
                        <line
                            x1="0"
                            x2={chartWidth}
                            class="stroke-current stroke-dasharray-2,2 opacity-30"
                        />
                        <text
                            x="-10"
                            dy="0.32em"
                            text-anchor="end"
                            class="fill-current">{tick}</text
                        >
                    </g>
                {/each}
                {#each [16, 20, 25, 30, 35, 40] as tick}
                    <g transform="translate({xScale(tick)}, {chartHeight})">
                        <text y="20" text-anchor="middle" class="fill-current"
                            >{tick}岁</text
                        >
                    </g>
                {/each}
                <line
                    x1="0"
                    y1={chartHeight}
                    x2={chartWidth}
                    y2={chartHeight}
                    class="stroke-current opacity-50"
                />
            </g>

            <!-- 波形曲线 -->
            <path
                d={pathData}
                fill="none"
                class="stroke-cyan-500 dark:stroke-cyan-400"
                stroke-width="2.5"
                stroke-linejoin="round"
                stroke-linecap="round"
            />

            <!-- 当前年龄的指示器 -->
            {#if currentPoint}
                <g class="indicator">
                    <line
                        x1={$indicatorCoords.x}
                        y1={$indicatorCoords.y}
                        x2={$indicatorCoords.x}
                        y2={chartHeight}
                        class="stroke-yellow-500 dark:stroke-yellow-400"
                        stroke-width="1.5"
                        stroke-dasharray="4 4"
                    />
                    <circle
                        cx={$indicatorCoords.x}
                        cy={$indicatorCoords.y}
                        r="6"
                        class="fill-yellow-500 dark:fill-yellow-400"
                    />
                    <circle
                        cx={$indicatorCoords.x}
                        cy={$indicatorCoords.y}
                        r="10"
                        class="fill-yellow-500/30 dark:fill-yellow-400/30"
                    />
                    <g
                        transform="translate({$indicatorCoords.x}, {$indicatorCoords.y})"
                    >
                        <rect
                            x="-22"
                            y="-30"
                            width="44"
                            height="22"
                            rx="4"
                            class="fill-gray-900 dark:fill-black opacity-80"
                        />
                        <text
                            text-anchor="middle"
                            y="-18"
                            class="fill-white font-bold text-sm"
                        >
                            {$indicatorCoords.value.toFixed(0)}
                        </text>
                    </g>
                </g>
            {/if}
        </g>
    </svg>
</div>

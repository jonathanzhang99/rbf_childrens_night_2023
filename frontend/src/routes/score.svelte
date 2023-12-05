<script lang="ts">
	export let score1: number;
	export let score2: number;
	export let gameMode: number;
</script>

{#if gameMode === 0}
	<h1>Score: {score1}</h1>
{:else}
	<h1>Player 1: {score1}</h1>
	<h1>Player 2: {score2}</h1>
{/if}

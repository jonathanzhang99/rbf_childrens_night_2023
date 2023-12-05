<script lang="ts">
	export let gameMode: number;
	export let countdownMs: number;

	$: title = gameMode === 0 ? 'Showdown' : 'Versus';
</script>

<h1>{title}</h1>
{#if countdownMs}
	<h2>{countdownMs / 1000}</h2>
{/if}

import React from 'react';
import {
	AbsoluteFill,
	Audio,
	interpolate,
	OffthreadVideo,
	Sequence,
	spring,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';
import {
	Captions,
	CtaStickers,
	Flash,
	FrostDust,
	FrostFrame,
	PriceHook,
	PromoStickers,
	SafeZoneGuide,
	ScentChips,
	Scrims,
	TitleCard,
	Vignette,
} from './Graphics';
import {SEGMENTS, TOTAL} from './words';

/** Punch-in zoom keyframes [frame, scale]. Origin is the product centre so it never leaves frame. */
const ZOOMS: [number, number][] = [
	[0, 1.06], // opening slam settles in
	[26, 1.1], // cut: "bukan RM300"
	[72, 1.04], // RM200
	[121, 1.0], // product reveal: pull back
	[178, 1.08], // cut: promo talk
	[302, 1.12], // "terus check out"
	[340, 1.02], // cut: scent
	[399, 1.08], // maskulin
	[477, 1.12], // cut: CTA
	[543, 1.12], // "terus beli"
];

const useZoom = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	let scale = ZOOMS[0][1];
	for (let i = 1; i < ZOOMS.length; i++) {
		const [kf, target] = ZOOMS[i];
		if (f < kf) break;
		const prev = ZOOMS[i - 1][1];
		const s = spring({frame: f - kf, fps, config: {damping: 15, stiffness: 240, mass: 0.6}});
		scale = prev + (target - prev) * s;
	}
	// opening: start extra tight and snap
	const open = spring({frame: f, fps, config: {damping: 14, stiffness: 200}});
	scale *= interpolate(open, [0, 1], [1.1, 1]);
	// gentle push-in drift for life
	scale *= 1 + (f / TOTAL) * 0.03;
	return scale;
};

const useShake = () => {
	const f = useCurrentFrame();
	const hits = [8, 43, 73, 104, 594];
	let x = 0;
	let y = 0;
	for (const h of hits) {
		const d = f - h;
		if (d >= 0 && d < 8) {
			const amp = (1 - d / 8) * (h === 104 ? 16 : 9);
			x += Math.sin(d * 2.7) * amp;
			y += Math.cos(d * 3.3) * amp;
		}
	}
	return {x, y};
};

type Sfx = [frame: number, name: string, vol: number];
const SFX: Sfx[] = [
	[0, 'deep_whoosh', 0.35],
	[6, 'hit', 0.45],
	[19, 'swipe', 0.5],
	[40, 'hit', 0.42],
	[59, 'swipe', 0.5],
	[71, 'hit', 0.48],
	[95, 'swipe', 0.5],
	[102, 'impact', 0.6],
	[116, 'whoosh', 0.45],
	[124, 'sparkle', 0.4],
	[164, 'shutter', 0.35],
	[176, 'swoosh', 0.35],
	[228, 'bubble', 0.5],
	[262, 'coins', 0.45],
	[300, 'swoosh', 0.3],
	[309, 'click', 0.6],
	[316, 'success', 0.3],
	[338, 'swoosh', 0.3],
	[399, 'pop', 0.35],
	[430, 'pop', 0.35],
	[447, 'pop', 0.35],
	[474, 'whoosh', 0.4],
	[517, 'notif', 0.45],
	[553, 'click', 0.45],
	[576, 'vacuum', 0.3],
	[592, 'hit', 0.45],
];

const Music: React.FC = () => {
	const f = useCurrentFrame();
	// Voice is -14 LUFS, BGM normalised to -14 LUFS → ~0.14 sits it ~17dB under the voice.
	const vol = interpolate(f, [0, 4, 600, 606, TOTAL - 1], [0.0, 0.14, 0.14, 0.32, 0.32], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	return <Audio src={staticFile('music/bgm.wav')} volume={vol} />;
};

export const BlackIce: React.FC<{showSafeZone: boolean}> = ({showSafeZone}) => {
	const scale = useZoom();
	const shake = useShake();
	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			{/* FOOTAGE (jump-cut segments) */}
			<AbsoluteFill
				style={{
					transform: `translate(${shake.x}px, ${shake.y}px) scale(${scale})`,
					transformOrigin: '540px 990px',
					filter: 'contrast(1.07) saturate(1.06) brightness(1.02)',
				}}
			>
				{SEGMENTS.map((s) => (
					<Sequence key={s.at} from={s.at} durationInFrames={s.to - s.from}>
						<OffthreadVideo src={staticFile('source.mp4')} trimBefore={s.from} muted />
					</Sequence>
				))}
			</AbsoluteFill>
			{/* cool ice grade */}
			<AbsoluteFill style={{background: 'rgba(40,120,200,0.07)', mixBlendMode: 'soft-light'}} />
			<Vignette />
			<Scrims />
			<FrostFrame />
			<FrostDust />

			{/* GRAPHICS */}
			<Sequence durationInFrames={122}>
				<PriceHook />
			</Sequence>
			<TitleCard from={121} to={184} />
			<Captions />
			<PromoStickers />
			<ScentChips />
			<CtaStickers />

			{/* transitions */}
			<Flash at={0} strength={0.9} len={7} />
			<Flash at={26} strength={0.35} len={4} />
			<Flash at={121} color="190,240,255" strength={0.95} len={10} />
			<Flash at={178} strength={0.35} len={4} />
			<Flash at={340} strength={0.35} len={4} />
			<Flash at={477} strength={0.4} len={5} />

			{showSafeZone ? <SafeZoneGuide /> : null}

			{/* AUDIO */}
			<Audio src={staticFile('voice.wav')} volume={1} />
			<Music />
			{SFX.map(([at, name, vol], i) => (
				<Sequence key={i} from={at} durationInFrames={Math.min(150, TOTAL - at)}>
					<Audio src={staticFile(`sfx/${name}.wav`)} volume={vol} />
				</Sequence>
			))}
		</AbsoluteFill>
	);
};

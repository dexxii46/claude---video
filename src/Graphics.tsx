import React from 'react';
import {
	AbsoluteFill,
	interpolate,
	random,
	spring,
	Easing,
} from 'remotion';
import {anton, C, mont, SAFE, useF, ZONE_LOW, ZONE_TOP} from './theme';
import {WORDS} from './words';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const useSpring = (start: number, cfg: object = {damping: 12, stiffness: 180, mass: 0.6}) => {
	const f = useF();
	const fps = 30;
	return spring({frame: f - start, fps, config: cfg});
};

/** Fade/scale out helper */
const outT = (f: number, end: number, len = 6) => interpolate(f, [end - len, end], [1, 0], clamp);

/* ---------------------------------------------------------------- HOOK */

const Price: React.FC<{
	label: string;
	inAt: number;
	strikeAt: number;
	parkAt: number; // when it shrinks into the "already crossed" row
	parkX: number;
}> = ({label, inAt, strikeAt, parkAt, parkX}) => {
	const f = useF();
	const slam = useSpring(inAt, {damping: 10, stiffness: 260, mass: 0.5});
	const park = useSpring(parkAt, {damping: 16, stiffness: 160});
	if (f < inAt) return null;
	const strike = interpolate(f, [strikeAt, strikeAt + 5], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const scale = interpolate(slam, [0, 1], [2.4, 1]) * interpolate(park, [0, 1], [1, 0.38]);
	const x = interpolate(park, [0, 1], [540, parkX]);
	const y = interpolate(park, [0, 1], [ZONE_TOP.y + 160, ZONE_TOP.y + 28]);
	const grey = interpolate(park, [0, 1], [0, 1]);
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				transform: `translate(-50%,-50%) scale(${scale})`,
				opacity: interpolate(slam, [0, 0.3], [0, 1], clamp) * interpolate(grey, [0, 1], [1, 0.75]),
			}}
		>
			<div
				style={{
					fontFamily: anton,
					fontSize: 230,
					lineHeight: 1,
					color: grey > 0.5 ? '#D9E4EA' : C.white,
					letterSpacing: 2,
					textShadow: `0 0 30px rgba(155,232,255,0.55), 0 10px 0 rgba(0,0,0,0.55)`,
					WebkitTextStroke: '3px rgba(0,0,0,0.35)',
					whiteSpace: 'nowrap',
					position: 'relative',
				}}
			>
				{label}
				<div
					style={{
						position: 'absolute',
						left: -14,
						top: '50%',
						height: 26,
						width: `calc(${strike * 100}% + 28px)`,
						background: C.red,
						borderRadius: 13,
						transform: 'rotate(-9deg)',
						boxShadow: '0 0 24px rgba(255,45,70,0.8)',
					}}
				/>
			</div>
		</div>
	);
};

const Stamp: React.FC<{at: number}> = ({at}) => {
	const f = useF();
	const s = useSpring(at, {damping: 9, stiffness: 300, mass: 0.6});
	if (f < at) return null;
	return (
		<div
			style={{
				position: 'absolute',
				left: 540,
				top: ZONE_TOP.y + 175,
				transform: `translate(-50%,-50%) rotate(-7deg) scale(${interpolate(s, [0, 1], [3, 1])})`,
				opacity: interpolate(s, [0, 0.25], [0, 1], clamp),
				background: C.yellow,
				color: C.black,
				fontFamily: anton,
				fontSize: 96,
				padding: '6px 34px 2px',
				borderRadius: 14,
				border: `6px solid ${C.black}`,
				boxShadow: '0 14px 40px rgba(0,0,0,0.5)',
				whiteSpace: 'nowrap',
			}}
		>
			TAK PAYAH!
		</div>
	);
};

export const PriceHook: React.FC = () => {
	const f = useF();
	const exit = interpolate(f, [114, 121], [0, 1], clamp);
	return (
		<AbsoluteFill
			style={{
				opacity: 1 - exit,
				transform: `translateY(${-exit * 120}px)`,
				filter: `blur(${exit * 12}px)`,
			}}
		>
			<Price label="RM400" inAt={6} strikeAt={20} parkAt={40} parkX={390} />
			<Price label="RM300" inAt={41} strikeAt={60} parkAt={72} parkX={690} />
			<Price label="RM200" inAt={72} strikeAt={96} parkAt={999} parkX={750} />
			<Stamp at={103} />
		</AbsoluteFill>
	);
};

/* ---------------------------------------------------------------- TITLE */

export const TitleCard: React.FC<{from: number; to: number}> = ({from, to}) => {
	const f = useF();
	const by = useSpring(from + 46);
	if (f < from || f > to) return null;
	const local = f - from;
	const exit = interpolate(f, [to - 7, to], [0, 1], clamp);
	const word = 'BLACK ICE'.split('');
	const shimmer = interpolate(local, [12, 40], [-40, 140], clamp);
	return (
		<AbsoluteFill style={{opacity: 1 - exit, transform: `scale(${1 + exit * 0.25})`}}>
			<div
				style={{
					position: 'absolute',
					top: ZONE_TOP.y + 10,
					width: '100%',
					textAlign: 'center',
					fontFamily: mont,
					fontWeight: 800,
					fontSize: 38,
					letterSpacing: interpolate(local, [0, 20], [30, 16], clamp),
					color: C.ice,
					opacity: interpolate(local, [0, 8], [0, 1], clamp),
					textShadow: '0 2px 12px rgba(0,0,0,0.7)',
				}}
			>
				PERFUME
			</div>
			<div
				style={{
					position: 'absolute',
					top: ZONE_TOP.y + 60,
					width: '100%',
					display: 'flex',
					justifyContent: 'center',
				}}
			>
				{word.map((ch, i) => {
					const t = interpolate(local, [4 + i * 1.6, 14 + i * 1.6], [0, 1], {
						...clamp,
						easing: Easing.out(Easing.cubic),
					});
					return (
						<span
							key={i}
							style={{
								fontFamily: anton,
								fontSize: 190,
								lineHeight: 1,
								display: 'inline-block',
								width: ch === ' ' ? 50 : undefined,
								opacity: t,
								filter: `blur(${(1 - t) * 14}px)`,
								transform: `translateY(${(1 - t) * 50}px) scale(${1.4 - t * 0.4})`,
								backgroundImage: `linear-gradient(100deg, #ffffff 0%, #d6f6ff ${shimmer - 18}%, #ffffff ${shimmer}%, ${C.ice} ${shimmer + 18}%, #ffffff 100%)`,
								WebkitBackgroundClip: 'text',
								backgroundClip: 'text',
								color: 'transparent',
							}}
						>
							{ch}
						</span>
					);
				})}
			</div>
			{/* glow layer behind letters */}
			<div
				style={{
					position: 'absolute',
					top: ZONE_TOP.y + 90,
					left: 140,
					right: 140,
					height: 140,
					background: 'radial-gradient(ellipse at center, rgba(47,184,255,0.45), transparent 70%)',
					filter: 'blur(20px)',
					zIndex: -1,
					opacity: interpolate(local, [6, 20], [0, 1], clamp),
				}}
			/>
			<div
				style={{
					position: 'absolute',
					top: ZONE_TOP.y + 262,
					width: '100%',
					display: 'flex',
					justifyContent: 'center',
					opacity: by,
					transform: `translateY(${(1 - by) * 20}px)`,
				}}
			>
				<div
					style={{
						fontFamily: mont,
						fontWeight: 800,
						fontSize: 34,
						color: C.black,
						background: C.ice,
						padding: '6px 22px',
						borderRadius: 999,
						letterSpacing: 4,
					}}
				>
					BY SUGAR BOMB
				</div>
			</div>
		</AbsoluteFill>
	);
};

/* ---------------------------------------------------------------- CAPTIONS */

// pages as [firstWordIndex, lastWordIndex]
const PAGES: [number, number][] = [
	[14, 17],
	[18, 20],
	[21, 23],
	[24, 25],
	[26, 28],
	[29, 30],
	[31, 34],
	[35, 37],
	[38, 39],
	[40, 43],
	[44, 46],
	[47, 50],
	[51, 53],
	[54, 55],
];

const HL: Record<string, string> = {
	kuning: C.yellow,
	promotion: C.yellow,
	'kau-kau,': C.yellow,
	check: C.ice,
	out: C.ice,
	maskulin: C.ice,
	'maskulin,': C.ice,
	'outdoor,': C.ice,
	indoor: C.ice,
	baucer: C.yellow,
	'habis.': C.red,
	'cepat-cepat': C.yellow,
};

export const Captions: React.FC = () => {
	const f = useF();
	const fps = 30;
	const LEAD = 2; // show words a hair early (feels in-sync on phones)
	const pageIdx = PAGES.findIndex(([a], i) => {
		const start = WORDS[a].s - LEAD;
		const next = PAGES[i + 1] ? WORDS[PAGES[i + 1][0]].s - LEAD : 1e9;
		return f >= start && f < next;
	});
	if (pageIdx < 0) return null;
	const [a, b] = PAGES[pageIdx];
	const pageStart = WORDS[a].s - LEAD;
	const enter = spring({frame: f - pageStart, fps, config: {damping: 14, stiffness: 220, mass: 0.5}});
	const words = WORDS.slice(a, b + 1);
	return (
		<div
			style={{
				position: 'absolute',
				top: ZONE_TOP.y + 70,
				left: 90,
				right: 90,
				display: 'flex',
				flexWrap: 'wrap',
				justifyContent: 'center',
				gap: '2px 16px',
				transform: `scale(${interpolate(enter, [0, 1], [0.8, 1])}) translateY(${(1 - enter) * 20}px)`,
				opacity: enter,
			}}
		>
			{words.map((w, i) => {
				const active = f >= w.s - LEAD;
				const pop = spring({frame: f - (w.s - LEAD), fps, config: {damping: 10, stiffness: 300, mass: 0.4}});
				const hl = HL[w.t.toLowerCase()];
				const isNow = active && f < w.e + 2;
				return (
					<span
						key={i}
						style={{
							fontFamily: mont,
							fontWeight: 900,
							fontSize: 64,
							lineHeight: 1.1,
							textTransform: 'uppercase',
							color: active ? hl ?? C.white : 'rgba(255,255,255,0.55)',
							transform: `scale(${active ? 1 + 0.12 * (1 - pop) + (isNow ? 0.04 : 0) : 0.96})`,
							display: 'inline-block',
							WebkitTextStroke: '8px #000',
							paintOrder: 'stroke fill',
							textShadow: '0 8px 18px rgba(0,0,0,0.55)',
						}}
					>
						{w.t.replace(/[.,]/g, '')}
					</span>
				);
			})}
		</div>
	);
};

/* ---------------------------------------------------------------- ICONS */

const Basket: React.FC<{size: number; color?: string}> = ({size, color = C.black}) => (
	<svg width={size} height={size} viewBox="0 0 64 64" fill="none">
		<path d="M18 26 L28 10 M46 26 L36 10" stroke={color} strokeWidth="5" strokeLinecap="round" />
		<path d="M8 26 H56 L50 54 H14 Z" fill={color} />
		<path d="M24 34 V46 M32 34 V46 M40 34 V46" stroke={C.yellow} strokeWidth="4" strokeLinecap="round" />
	</svg>
);

const Check: React.FC<{size: number; color?: string; progress?: number}> = ({size, color = C.black, progress = 1}) => (
	<svg width={size} height={size} viewBox="0 0 24 24" fill="none">
		<path
			d="M5 12.5 L10 17.5 L19 7"
			stroke={color}
			strokeWidth="3.4"
			strokeLinecap="round"
			strokeLinejoin="round"
			strokeDasharray={24}
			strokeDashoffset={24 * (1 - progress)}
		/>
	</svg>
);

/* ---------------------------------------------------------------- PROMO SECTION (low zone) */

const Pill: React.FC<{
	at: number;
	until: number;
	x: number;
	children: React.ReactNode;
	bg: string;
	color?: string;
	fromX?: number;
	rotate?: number;
}> = ({at, until, x, children, bg, color = C.black, fromX = 0, rotate = 0}) => {
	const f = useF();
	const s = useSpring(at, {damping: 11, stiffness: 220, mass: 0.5});
	if (f < at || f > until) return null;
	const o = outT(f, until);
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: ZONE_LOW.y,
				height: ZONE_LOW.h - 6,
				display: 'flex',
				alignItems: 'center',
				gap: 14,
				padding: '0 26px 0 14px',
				background: bg,
				color,
				borderRadius: 26,
				fontFamily: mont,
				fontWeight: 900,
				fontSize: 40,
				whiteSpace: 'nowrap',
				boxShadow: '0 12px 30px rgba(0,0,0,0.45)',
				transform: `translateX(${(1 - s) * fromX}px) scale(${interpolate(s, [0, 1], [0.4, 1]) * (0.8 + 0.2 * o)}) rotate(${rotate * s}deg)`,
				transformOrigin: 'left center',
				opacity: Math.min(interpolate(s, [0, 0.3], [0, 1], clamp), o),
			}}
		>
			{children}
		</div>
	);
};

export const PromoStickers: React.FC = () => {
	const f = useF();
	// checkout button press
	const press = interpolate(f, [309, 312, 316], [1, 0.9, 1], clamp);
	const ripple = interpolate(f, [310, 326], [0, 1], clamp);
	const tick = interpolate(f, [316, 324], [0, 1], clamp);
	return (
		<AbsoluteFill>
			<Pill at={228} until={298} x={SAFE.left + 20} bg={C.yellow} fromX={-200}>
				<Basket size={70} />
				BAKUL KUNING
			</Pill>
			<Pill at={264} until={298} x={530} bg={C.red} color={C.white} fromX={300} rotate={-3}>
				<span style={{fontFamily: anton, fontSize: 54, fontWeight: 400}}>%</span>
				PROMO KAW²
			</Pill>
			{f >= 301 && f <= 342 ? (
				<div
					style={{
						position: 'absolute',
						left: 540 - 25,
						top: ZONE_LOW.y,
						transform: `translateX(-50%) scale(${press * spring({frame: f - 301, fps: 30, config: {damping: 11, stiffness: 220}}) * outT(f, 342)})`,
					}}
				>
					<div
						style={{
							display: 'flex',
							alignItems: 'center',
							gap: 16,
							height: ZONE_LOW.h - 6,
							padding: '0 40px',
							borderRadius: 999,
							background: `linear-gradient(90deg, ${C.yellow}, #FFB800)`,
							fontFamily: mont,
							fontWeight: 900,
							fontSize: 46,
							color: C.black,
							boxShadow: '0 12px 30px rgba(0,0,0,0.5)',
							position: 'relative',
							whiteSpace: 'nowrap',
						}}
					>
						<div
							style={{
								width: 56,
								height: 56,
								borderRadius: 28,
								background: C.black,
								display: 'flex',
								alignItems: 'center',
								justifyContent: 'center',
							}}
						>
							<Check size={42} color={C.yellow} progress={tick} />
						</div>
						CHECKOUT SEKARANG
						<div
							style={{
								position: 'absolute',
								left: '50%',
								top: '50%',
								width: 200,
								height: 200,
								marginLeft: -100,
								marginTop: -100,
								borderRadius: 100,
								border: '6px solid white',
								transform: `scale(${ripple * 2.2})`,
								opacity: ripple > 0 ? 1 - ripple : 0,
							}}
						/>
					</div>
				</div>
			) : null}
		</AbsoluteFill>
	);
};

/* ---------------------------------------------------------------- SCENT CHIPS */

const Chip: React.FC<{at: number; x: number; label: string}> = ({at, x, label}) => {
	const f = useF();
	const s = useSpring(at, {damping: 10, stiffness: 260, mass: 0.5});
	if (f < at) return null;
	const o = outT(f, 474);
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: ZONE_LOW.y + 6,
				height: ZONE_LOW.h - 18,
				display: 'flex',
				alignItems: 'center',
				gap: 8,
				padding: '0 22px 0 12px',
				borderRadius: 999,
				background: 'rgba(5,8,12,0.78)',
				border: `3px solid ${C.ice}`,
				boxShadow: `0 0 22px rgba(155,232,255,0.45)`,
				color: C.white,
				fontFamily: mont,
				fontWeight: 900,
				fontSize: 36,
				transform: `translateY(${(1 - s) * 60}px) scale(${interpolate(s, [0, 1], [0.5, 1]) * (0.85 + 0.15 * o)})`,
				opacity: Math.min(interpolate(s, [0, 0.3], [0, 1], clamp), o),
			}}
		>
			<div
				style={{
					width: 50,
					height: 50,
					borderRadius: 25,
					background: C.ice,
					display: 'flex',
					alignItems: 'center',
					justifyContent: 'center',
				}}
			>
				<Check size={38} progress={interpolate(f, [at + 2, at + 9], [0, 1], clamp)} />
			</div>
			{label}
		</div>
	);
};

export const ScentChips: React.FC = () => (
	<AbsoluteFill>
		<Chip at={399} x={SAFE.left + 10} label="MASKULIN" />
		<Chip at={430} x={358} label="OUTDOOR" />
		<Chip at={447} x={638} label="INDOOR" />
	</AbsoluteFill>
);

/* ---------------------------------------------------------------- CTA */

export const CtaStickers: React.FC = () => {
	const f = useF();
	// Simple, clean CTA: one pill, gentle fade/slide in, no extra motion.
	const t = interpolate(f, [477, 487], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	if (f < 477) return null;
	return (
		<AbsoluteFill>
			<div
				style={{
					position: 'absolute',
					left: SAFE.left + 20,
					top: ZONE_LOW.y,
					height: ZONE_LOW.h - 6,
					display: 'flex',
					alignItems: 'center',
					gap: 14,
					padding: '0 30px 0 16px',
					background: C.yellow,
					color: C.black,
					borderRadius: 26,
					fontFamily: mont,
					fontWeight: 900,
					fontSize: 40,
					whiteSpace: 'nowrap',
					boxShadow: '0 10px 26px rgba(0,0,0,0.4)',
					opacity: t,
					transform: `translateY(${(1 - t) * 24}px)`,
				}}
			>
				<Basket size={64} />
				TEKAN BAKUL KUNING
			</div>
		</AbsoluteFill>
	);
};

/* ---------------------------------------------------------------- FX */

export const Flash: React.FC<{at: number; color?: string; len?: number; strength?: number}> = ({
	at,
	color = '255,255,255',
	len = 8,
	strength = 0.85,
}) => {
	const f = useF();
	const o = interpolate(f, [at, at + 1, at + len], [0, strength, 0], clamp);
	if (o <= 0) return null;
	return (
		<AbsoluteFill
			style={{
				background: `radial-gradient(circle at 50% 50%, rgba(${color},${o}) 0%, rgba(${color},${o * 0.6}) 60%, rgba(${color},${o * 0.3}) 100%)`,
				mixBlendMode: 'screen',
			}}
		/>
	);
};

/** Ice dust drifting up along the edges only (never over the product). */
export const FrostDust: React.FC = () => {
	const f = useF();
	const boost = interpolate(f, [119, 128, 178, 200], [0.35, 1, 1, 0.35], clamp);
	const N = 34;
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{new Array(N).fill(0).map((_, i) => {
				const side = i % 2 === 0;
				const x = side ? 10 + random(`x${i}`) * 170 : 900 + random(`x${i}`) * 170;
				const speed = 1.2 + random(`s${i}`) * 2.4;
				const y = 1920 - ((random(`y${i}`) * 1920 + f * speed) % 1920);
				const size = 3 + random(`r${i}`) * 7;
				const tw = 0.5 + 0.5 * Math.sin(f / (4 + random(`t${i}`) * 6) + i);
				return (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: x + Math.sin(f / 20 + i) * 12,
							top: y,
							width: size,
							height: size,
							borderRadius: size,
							background: '#E6FAFF',
							boxShadow: `0 0 ${size * 2.5}px ${C.ice}`,
							opacity: boost * tw * 0.8,
						}}
					/>
				);
			})}
		</AbsoluteFill>
	);
};

/** Frosted corners during the product reveal (edges only). */
export const FrostFrame: React.FC = () => {
	const f = useF();
	const o = interpolate(f, [119, 126, 172, 184], [0, 1, 1, 0], clamp);
	if (o <= 0) return null;
	return (
		<AbsoluteFill
			style={{
				opacity: o,
				background:
					'radial-gradient(ellipse 75% 60% at 50% 52%, transparent 62%, rgba(155,232,255,0.22) 82%, rgba(220,248,255,0.55) 100%)',
			}}
		/>
	);
};

export const Vignette: React.FC = () => (
	<AbsoluteFill
		style={{
			background: 'radial-gradient(ellipse 85% 70% at 50% 52%, transparent 55%, rgba(0,0,0,0.42) 100%)',
		}}
	/>
);

/** Top scrim so white text reads on the bright car bonnet; low scrim for stickers. */
export const Scrims: React.FC = () => (
	<AbsoluteFill>
		<div
			style={{
				position: 'absolute',
				top: 0,
				left: 0,
				right: 0,
				height: 700,
				background: 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.25) 70%, transparent 100%)',
			}}
		/>
	</AbsoluteFill>
);

export const SafeZoneGuide: React.FC = () => (
	<AbsoluteFill style={{pointerEvents: 'none'}}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: SAFE.top, background: 'rgba(255,0,0,0.28)'}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: SAFE.bottom, bottom: 0, background: 'rgba(255,0,0,0.28)'}} />
		<div style={{position: 'absolute', left: SAFE.right, right: 0, top: 860, bottom: 0, background: 'rgba(255,0,0,0.28)'}} />
		<div style={{position: 'absolute', left: 0, width: SAFE.left, top: 0, bottom: 0, background: 'rgba(255,0,0,0.28)'}} />
		<div
			style={{
				position: 'absolute',
				left: 300,
				top: 570,
				width: 480,
				height: 840,
				border: '4px dashed rgba(0,255,120,0.9)',
				color: 'rgba(0,255,120,0.95)',
				fontFamily: mont,
				fontWeight: 800,
				fontSize: 28,
				padding: 10,
			}}
		>
			PRODUCT ZONE
		</div>
	</AbsoluteFill>
);

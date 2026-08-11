import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {Gif} from '@remotion/gif';
import mapping from '../mapping.json';

// Style rules baked in (see skills/pimp/references/style-rules.md):
// hard cuts only — NO transitions, NO zoom, NO shadow, NO text overlays.
type Seg = {
	start: number;
	end?: number;
	type?: string;
	image?: string;
	images?: string[];
	format?: string;
	align?: string;
};

const Media: React.FC<{src: string; style: React.CSSProperties}> = ({src, style}) =>
	src.toLowerCase().endsWith('.gif') ? (
		<Gif src={staticFile(src)} style={style} fit="cover" />
	) : (
		<Img src={staticFile(src)} style={style} />
	);

const ImgCut: React.FC<{seg: Seg; top: number; shadow: boolean}> = ({seg, top, shadow}) => {
	// Square is the default: the reference format keeps every cutaway consistent.
	// 'landscape' is the justified exception (wide compositions that a square crop would destroy).
	const square = seg.format !== 'landscape';
	const w = square ? Math.round(mapping.width * 0.41) : Math.round(mapping.width * 0.519);
	const h = square ? w : Math.round(w * 0.575);
	const justify =
		seg.align === 'left' ? 'flex-start' : seg.align === 'right' ? 'flex-end' : 'center';
	return (
		<div
			style={{
				position: 'absolute',
				top,
				left: 0,
				right: 0,
				display: 'flex',
				justifyContent: justify,
				paddingLeft: seg.align === 'left' ? 64 : 0,
				paddingRight: seg.align === 'right' ? 64 : 0,
			}}
		>
			<div
				style={{
					width: w,
					height: h,
					borderRadius: 4,
					overflow: 'hidden',
					boxShadow: shadow ? '0 10px 28px rgba(0,0,0,.28)' : undefined,
				}}
			>
				<Media
					src={seg.image as string}
					style={{width: '100%', height: '100%', objectFit: 'cover'}}
				/>
			</div>
		</div>
	);
};

const Collage: React.FC<{images: string[]}> = ({images}) => (
	<div
		style={{
			position: 'absolute',
			top: 44,
			left: '16%',
			width: '68%',
			display: 'grid',
			gridTemplateColumns: 'repeat(3, 1fr)',
			gap: 4,
		}}
	>
		{images.slice(0, 6).map((im, i) => (
			<div
				key={i}
				style={{aspectRatio: '1', borderRadius: 4, overflow: 'hidden'}}
			>
				<Media src={im} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
			</div>
		))}
	</div>
);

export const ReelCutaways: React.FC = () => {
	const segs = mapping.segments as Seg[];
	const top = (mapping as {imageTop?: number}).imageTop ?? 235;
	const shadow = (mapping as {imageShadow?: boolean}).imageShadow === true;
	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			<OffthreadVideo src={staticFile(mapping.rush)} />
			{segs.map((seg, i) => {
				const end = seg.end ?? segs[i + 1]?.start ?? mapping.durationInFrames;
				return (
					<Sequence key={i} from={seg.start} durationInFrames={end - seg.start}>
						{seg.type === 'collage' ? (
							<Collage images={seg.images as string[]} />
						) : (
							<ImgCut seg={seg} top={top} shadow={shadow} />
						)}
					</Sequence>
				);
			})}
		</AbsoluteFill>
	);
};

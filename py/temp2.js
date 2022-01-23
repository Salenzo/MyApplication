class tile {
	constructor({row: e, col: n, tileKey: t, heightType: a, buildableType: r, passableMask: i, map: o}) {
		this.map = o;
		this.row = e;
		this.col = n;
		this.tileKey = t;
		this.heightType = a;
		this.buildableType = r;
		this.passableMask_raw = i;
		this.passableMaskOverride = null;
		this.visited = false;
		this.pointer = null;
	}
	get passableMask() {
		return this.passableMaskOverride || this.passableMask_raw;
	}
}

class ppmap {
	constructor({tiles, width, height}, {routes, predefines}) {
		this.tiles_ref = tiles.slice();
		this.width = width;
		this.height = height;
		this.tiles = Array(height).fill().map(((_, t)=>Array(width).fill().map(((_, a) => new tile(Object.assign({}, this.tiles_ref[t * width + a], {row: t, col: a, map: this}))))));
    // 放箱子时只检查有类型0检查点的路径，且只检查沿着类型0检查点能否通行（允许斜向）。
		if (predefines && predefines.tokenInsts) {
			predefines.tokenInsts.forEach(({position, hidden, inst: {characterKey}}) => {
			  if (hidden || ["箱子ID等"].includes(characterKey)) {
		      this.tiles[position.row][position.col].passableMaskOverride = 2;
        }
			});
		}
	}
	getTileAt({row, col}) {
		return row < 0 || col < 0 || row >= this.height || col >= this.width ? null : this.tiles[row][col];
	}
	getAvailableNeighbours(tile, {allow_diagonal, motionMode}) {
    const t = [
			{row: tile.row + 1, col: tile.col},
			{row: tile.row + 1, col: tile.col + 1},
			{row: tile.row, col: tile.col + 1},
			{row: tile.row - 1, col: tile.col + 1},
			{row: tile.row - 1, col: tile.col},
			{row: tile.row - 1, col: tile.col - 1},
			{row: tile.row, col: tile.col - 1},
			{row: tile.row + 1, col: tile.col - 1},
    ].map((t, direction) => {
      t = tile.map.getTileAt(t)
      return {
        dist: (direction % 2 ? 1.414 : 1) + (allow_diagonal && t && "tile_yinyang_switch" === t.tileKey ? -1 : 0),
        tile: t,
        DIRE: direction,
      };
    });
    [0, 2, 4, 6].map(direction => {
      if (!checkTilePassable(t[direction].tile, motionMode)) {
        t[direction].tile = null;
        t[(direction + 1) % 8].tile = null;
        t[(direction + 7) % 8].tile = null;
      }
    });
    if (!allow_diagonal) t = [t[0], t[2], t[4], t[6]];
    return t.filter(({tile}) => checkTilePassable(tile, motionMode));
	}
	// motionMode：地面0还是飞行1
	findPathBetween(from, to, {motionMode, allow_diagonal, point_data}) {
		if (from.row < 0 || from.col < 0 || from.row >= this.height || from.col >= this.width || to.row < 0 || to.col < 0 || to.row >= this.height || to.col >= this.width) return null;
		let path = null;
		const queue = [{dist: 0, tile: this.getTileAt(from)}];
		while (queue.length) {
			const {dist: head_dist, tile: head_tile} = queue.shift();
			head_tile.visited = true;
			if (head_tile.row === to.row && head_tile.col === to.col) {
        // connect pointers
        path = [{row: head_tile.row, col: head_tile.col}];
        let p = head_tile;
        while (p.pointer) {
          path.unshift({row: p.pointer.tile.row, col: p.pointer.tile.col}),
          p = p.pointer.tile;
        }
				break;
			}
			this.getAvailableNeighbours(head_tile, {motionMode, allow_diagonal}).filter(x => !x.tile.visited).forEach(({dist, tile, DIRE}) => {
        if (!tile.pointer || (dist + head_dist < tile.pointer.dist || dist + head_dist === tile.pointer.dist && DIRE < tile.pointer.direction)) {
          tile.pointer = {tile: head_tile, dist: dist + head_dist, direction: DIRE};
        }
				if (!queue.length || queue[queue.length - 1].dist < head_dist) {
					queue.push({dist: head_dist + dist, tile: tile});
					return;
				}
				let a = queue.length;
				while (a > 0 && queue[a - 1].dist > head_dist) a--;
				queue.splice(a, 0, {dist: head_dist + dist, tile: tile});
			});
		}
    Array(this.height).fill().forEach((_, row) =>
			Array(this.width).fill().forEach((_, col) => {
        this.tiles[row][col].visited = false;
        this.tiles[row][col].pointer = null;
      })
		);
		if (!path) throw new Error("Invalid path");
		path[0].reachOffset = from.reachOffset;
		path[path.length - 1].reachOffset = to.reachOffset;
		if ([1, 3, 5].includes(to.type)) Object.assign(path[path.length - 1], point_data);
		return path;
	}
	findPath({startPosition, checkpoints, endPosition, motionMode, allowDiagonalMove}) {
		let _ = null;
		const u = [startPosition, ...checkpoints.map(({position: {row: e, col: n}, reachOffset: t, type: a, time: r}) => ({row: e, col: n, type: a,time: r, reachOffset: t})), endPosition].map(e => {
			if ([1, 3, 5, 7].includes(e.type)) {
				return Object.assign({}, e, {
					row: _.row,
					col: _.col,
					reachOffset: _.reachOffset
				});
			} else {
				_ = e;
				return e;
			}
		});
		if (u.some(e => !checkTilePassable(this.getTileAt(e), motionMode))) return u;
		const s = [];
		for (let e = 0; e < u.length - 1; e++) {
			if ([5, 6].includes(u[e].type)) s.push(Object.assign({}, u[e]));
			if ([5, 6].includes(u[e + 1].type)) continue;
			const n = this.findPathBetween(u[e], u[e + 1], {
				motionMode,
				allow_diagonal: allowDiagonalMove,
				point_data: u[e + 1],
			});
			const t = this.merge(n, {motionMode});
			if (e) t.unshift();
			s.push(...t);
		}
		return s;
	}
	checkArea({from, to, motionMode}) {
		const col0 = Math.min(from.col, to.col);
		const row0 = Math.min(from.row, to.row);
		return Array(Math.abs(from.row - to.row) + 1).fill().every((_, row) =>
			Array(Math.abs(from.col - to.col) + 1).fill().every((_, col) =>
				checkTilePassable(this.tiles[row0 + row][col0 + col], motionMode)
			)
		);
	}
	merge(list, {motionMode}) {
		if (list.length <= 2) return list;
		let [from, ...rest] = list, r = null;
		const t = [from];
		rest.forEach(e => {
      if (this.checkArea({from: from, to: e, motionMode})) {
        r = e;
      } else {
        t.push(r);
        from = r;
        if (this.checkArea({from: from, to: e, motionMode})) r = e;
      };
		});
		t.push(list[list.length - 1]);
		return t;
	}
}

function checkTilePassable(tile, motionMode) {
  return tile && tile.passableMask & 1 << motionMode && (motionMode || !["tile_hole", "tile_empty"].includes(tile.tileKey))
}

const level_act16d5_ex06 = JSON.parse(require("fs").readFileSync("level_act16d5_ex06.json"));
const pp=new ppmap(level_act16d5_ex06.mapData, level_act16d5_ex06);
console.log(pp.findPath(
  {
    startPosition: { row: 1, col: 0 },
    checkpoints: [{ position: { row: 1, col: 1 } }, { position: { row: 7, col: 1 } }],
    endPosition: { row: 8, col: 10 },
    motionMode: 0,
    allowDiagonalMove: true,
  }
));

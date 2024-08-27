import type { DisplayObjectWithCulling, AABB } from "./types";

export interface SimpleOptions {
	visible?: string;
	dirtyTest?: boolean;
}

const defaultSimpleOptions = {
	visible: "visible",
	dirtyTest: false
};

export interface SimpleStats {
	total: number;
	visible: number;
	culled: number;
}

type DisplayObjectWithCullingArray = DisplayObjectWithCulling[] & {
	staticObject?: boolean;
};

export class Simple {
	public options: SimpleOptions;
	public dirtyTest: boolean;
	protected lists: DisplayObjectWithCulling[];

	constructor(options: SimpleOptions = {}) {
		options = { ...defaultSimpleOptions, ...options };
		this.dirtyTest =
			typeof options.dirtyTest !== "undefined" ? options.dirtyTest : true;
		this.lists = [];
	}

	addList(
		array: DisplayObjectWithCullingArray,
		staticObject?: boolean
	): object[] {
		for (let i = 0; i < array.length; i++) {
			if (array[i].children.length > 0) {
				for (let j = 0; j < array[i].children.length; j++) {
					this.lists.push(array[i].children[j]);
				}
			} else {
				this.lists.push(array[i]);
			}
		}

		if (staticObject) {
			array.staticObject = true;
		}
		for (let i = 0; i < this.lists.length; i++) {
			this.updateObject(this.lists[i]);
		}
		return array;
	}

	removeList(
		array: DisplayObjectWithCullingArray
	): DisplayObjectWithCullingArray {
		for (let i = 0; i < array.length; i++) {
			const index = this.lists.indexOf(array[i]);
			if (index !== -1) {
				this.lists.splice(index, 1);
			}
		}
		return array;
	}

	add(
		object: DisplayObjectWithCulling,
		staticObject?: boolean
	): DisplayObjectWithCulling {
		if (staticObject) {
			object.staticObject = true;
		}
		if (this.dirtyTest || staticObject) {
			this.updateObject(object);
		}
		this.lists.push(object);
		return object;
	}

	remove(object: DisplayObjectWithCulling): DisplayObjectWithCulling {
		const index = this.lists.indexOf(object);
		if (index === -1) {
			return object;
		}
		this.lists.splice(index, 1);
		return object;
	}

	cull(bounds: AABB, skipUpdate?: boolean) {
		if (!skipUpdate) {
			this.updateObjects();
		}

		const boundX = bounds.x;
		const boundY = bounds.y;
		const boundWidth = bounds.width;
		const boundHeight = bounds.height;
		const boundRight = boundX + boundWidth;
		const boundBottom = boundY + boundHeight;

		for (const object of this.lists) {
			const box = object.AABB; // Use cached AABB
			const boxRight = box.x + box.width;
			const boxBottom = box.y + box.height;
			object.visible =
				boxRight > boundX &&
				box.x < boundRight &&
				boxBottom > boundY &&
				box.y < boundBottom;
		}
	}

	updateObjects() {
		if (this.dirtyTest) {
			for (const object of this.lists) {
				if (!object.staticObject && object.dirty) {
					this.updateObject(object);
					object.dirty = false;
				}
			}
		} else {
			for (const object of this.lists) {
				if (!object.staticObject) {
					this.updateObject(object);
				}
			}
		}
	}

	updateObject(object: DisplayObjectWithCulling) {
		const box = object.getLocalBounds();
		object.AABB = object.AABB || { x: 0, y: 0, width: 0, height: 0 };
		object.AABB.x =
			object.x + (box.x - object.pivot.x) * Math.abs(object.scale.x);
		object.AABB.y =
			object.y + (box.y - object.pivot.y) * Math.abs(object.scale.y);
		object.AABB.width = box.width * Math.abs(object.scale.x);
		object.AABB.height = box.height * Math.abs(object.scale.y);
	}

	query(bounds: AABB): DisplayObjectWithCulling[] {
		let results = [];
		for (let object of this.lists) {
			const box = object.AABB;
			if (
				box &&
				box.x + box.width > bounds.x &&
				box.x - box.width < bounds.x + bounds.width &&
				box.y + box.height > bounds.y &&
				box.y - box.height < bounds.y + bounds.height
			) {
				results.push(object);
			}
		}
		return results;
	}

	queryCallback(
		bounds: AABB,
		callback: (object: DisplayObjectWithCulling) => boolean
	): boolean {
		for (let object of this.lists) {
			const box = object.AABB;
			if (
				box &&
				box.x + box.width > bounds.x &&
				box.x - box.width < bounds.x + bounds.width &&
				box.y + box.height > bounds.y &&
				box.y - box.height < bounds.y + bounds.height
			) {
				if (callback(object)) {
					return true;
				}
			}
		}
		return false;
	}

	stats(): SimpleStats {
		let visible = 0,
			count = 0;
		for (let object of this.lists) {
			visible += object.visible ? 1 : 0;
			count++;
		}
		return { total: count, visible, culled: count - visible };
	}
}

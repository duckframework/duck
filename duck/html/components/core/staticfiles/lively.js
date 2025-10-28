"use strict";

/**
 * Lively.js – Duck Framework Client Patch & Navigation System
 * Performance-optimized implementation for patching, navigation, and WebSocket communication.
 * 
 * Notes
 * - This system doesn't modify any untracked props (props which doesn't come with the components) plus private props.
 * - But for style, it's the same as what happens to props.
 * - When using Lively, make sure DOM changes are done within the system as any DOM mutation outside Lively will be detected and an error will be shown.  
 *
 * @author Brian Musakwa <digreatbrian@gmail.com>
 * @version 1.0.0
 */

/**
 * WebSocket opcodes based on RFC 6455.
 * @readonly
 */
const WebSocketCodes = {
  CONTINUATION: 0x0,
  TEXT: 0x1,
  BINARY: 0x2,
  CLOSE: 0x8,
  PING: 0x9,
  PONG: 0xA,
};

/**
 * WebSocket close status codes (RFC 6455 Section 7.4).
 * @readonly
 */
const WebSocketCloseCodes = {
  NORMAL_CLOSURE: 1000,
  GOING_AWAY: 1001,
  PROTOCOL_ERROR: 1002,
  UNSUPPORTED_DATA: 1003,
  NO_STATUS_RCVD: 1005,
  ABNORMAL_CLOSURE: 1006,
  INVALID_DATA: 1007,
  POLICY_VIOLATION: 1008,
  MESSAGE_TOO_BIG: 1009,
  MANDATORY_EXTENSION: 1010,
  INTERNAL_ERROR: 1011,
  SERVICE_RESTART: 1012,
  TRY_AGAIN_LATER: 1013,
  BAD_GATEWAY: 1014,
  TLS_HANDSHAKE: 1015,
};

/**
 * Patch operation codes.
 * @readonly
 */
const PatchCodes = {
  REPLACE_NODE: 0,
  REMOVE_NODE: 1,
  INSERT_NODE: 2,
  ALTER_TEXT: 3,
  REPLACE_PROPS: 4,
  REPLACE_STYLE: 5,
};

/**
 * Event operation codes for WebSocket events.
 * @readonly
 */
const EventOpCodes = {
  APPLY_PATCH: 1,
  DISPATCH_COMPONENT_EVENT: 100,
  EXECUTE_JS: 101,
  JS_EXECUTION_RESULT: 111,
  NAVIGATE_TO: 120,
  NAVIGATION_RESULT: 121,
  COMPONENT_UNKNOWN: 150,
};

EventOpCodes.CLIENT_EVENT_OPCODES = new Set([
  EventOpCodes.APPLY_PATCH,
  EventOpCodes.EXECUTE_JS,
  EventOpCodes.NAVIGATION_RESULT,
  EventOpCodes.COMPONENT_UNKNOWN,
]);

/**
  * Duck Exceptions
  */

/**
  * Base exception for all Duck exceptions
  */
class BaseError extends Error {
  constructor(message) {
    super(message);
    this.name = "BaseError";
  }
}

/**
  * Base Lively exception.
  */
class LivelyError extends BaseError {
  constructor(message) {
    super(message);
    this.name = "LivelyError";
  }
}

/**
  * Exception raised when registering an element by UID fails.
  */
class ElementRegistrationError extends LivelyError {
  constructor(message) {
    super(message);
    this.name = "ElementRegistrationError";
  }
}

/**
 * Utility for encoding/decoding MessagePack.
 */
class Msgpack {
  static encode(data) {
    return msgpack.encode(data);
  }

  static decode(data) {
    return msgpack.decode(new Uint8Array(data));
  }
}

/**
 * LRUCache - Fast Least Recently Used (LRU) cache for JS clients
 *
 * Stores up to `maxSize` items. On overflow, removes least recently used item.
 * Uses native Map for O(1) get/set and ordering.
 *
 * Example usage:
 *   const cache = new LRUCache(100);
 *   cache.set('key', value);
 *   const v = cache.get('key');
 *
 * @class
 */
class LRUCache {
  /**
   * Create an LRUCache.
   * @param {number} maxSize - Maximum items to keep in cache. Recommended: 50-200 for most JS clients.
   */
  constructor(maxSize) {
    if (!Number.isInteger(maxSize) || maxSize <= 0) {
      throw new Error('LRUCache: maxSize must be a positive integer');
    }
    this.maxSize = maxSize;
    this.cache = new Map();
  }

  /**
   * Get the value for a key. Marks as most recently used.
   * @param {string|number} key
   * @returns {*} value or undefined if not present
   */
  get(key) {
    if (!this.cache.has(key)) return undefined;
    const value = this.cache.get(key);
    // Move to end to mark as recently used
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  /**
   * Set a value for a key. If cache is full, removes least recently used item.
   * @param {string|number} key
   * @param {*} value
   */
  set(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    else if (this.cache.size >= this.maxSize) {
      // Remove least recently used (first key)
      const lru = this.cache.keys().next().value;
      this.cache.delete(lru);
    }
    this.cache.set(key, value);
  }

  /**
   * Check if a key exists in cache.
   * @param {string|number} key
   * @returns {boolean}
   */
  has(key) {
    return this.cache.has(key);
  }

  /**
   * Remove a key from cache.
   * @param {string|number} key
   */
  delete(key) {
    this.cache.delete(key);
  }

  /**
   * Clear all cache entries.
   */
  clear() {
    this.cache.clear();
  }

  /**
   * Number of items in cache.
   * @returns {number}
   */
  size() {
    return this.cache.size;
  }
}

/**
 * Monitors DOM mutations affecting "Lively" attributes/elements relevant to the patch system,
 * and warns if a user or script makes changes outside the server-driven patch API.
 * 
 * - Observes only data-uid, data-events, data-document-events attribute changes
 * - Observes addition/removal of DOM elements
 * - Ignores changes made while the patch system is running (using patcher.patchInProgressCounter)
 * - Throttles warning to avoid user spam
 */
class DOMObserver {
  constructor (patcher) {
    if (!patcher) {
      throw new LivelyError("Patcher argument required.");
    }
    this.LIVELY_ATTRS = ["data-uid", "data-events", "data-document-events"];
    this.patcher = patcher;
    this.warningTimeout = null;
    this.COOLDOWN_MS = 5000;
  }
  
  /** Observes DOM mutations and triggers warnings for untracked changes.
   * Skips mutations caused during sys patch application.
   */
  observe(){
    this.observer = new MutationObserver((mutations) => {
      // patcher.patchInProgress should be a counter, not boolean
      if (this.patcher.patchInProgress) {
        // System patch in progress, skip
        return;
      }
      for (const mutation of mutations) {
        const { relevant, reason } = this.isRelevantSysMutation(mutation);
        if (relevant) {
          this.showWarningToUserOnce(mutation, reason);
          break;
        }
      }
    });
    
    // Observe the entire document for changes to sys attributes or element insert/removal
    this.observer.observe(document.body, {
      attributes: true,
      attributeFilter: this.LIVELY_ATTRS,
      childList: true,
      characterData: false,
      subtree: true,
    });
  }
  
  /**
   * Displays a warning to the user and logs a detailed message to the console.
   * @param {MutationRecord} mutation - The detected mutation record
   * @param {string} [reason] - Human-readable reason for the warning
   */
  showWarningToUser(mutation, reason) {
    // Visual warning (toast, modal, etc.)
    alert(
      "⚠️ Warning: Untracked DOM change detected!\n" +
      (reason ? reason + "\n" : "") +
      "Changes to lively-managed elements may be lost or cause display issues. " +
      "Please use the Lively API for all modifications."
    );
  
    // Developer log (for debugging)
    console.warn(
      "[Lively] Untracked DOM mutation detected:",
      {
        reason: reason || "Unknown reason",
        mutation
      }
    );
  }
  
  /**
   * Shows the warning only once per cooldown period.
   * @param {MutationRecord} mutation - Mutation to show warning for
   * @param {string} reason - Reason to show
   */
  showWarningToUserOnce(mutation, reason) {
    if (!this.warningTimeout) {
      this.showWarningToUser(mutation, reason);
      this.warningTimeout = setTimeout(() => {
        this.warningTimeout = null;
      }, this.COOLDOWN_MS);
    }
  }
  
  /**
   * Determines if a mutation (a change to the webpage's structure) is something our system cares about.
   * Our system, "Lively" component system, uses special elements marked with a "data-uid" attribute.
   * This function helps us ignore changes we don't need to worry about, making our system more efficient.
   *
   * Here's what this function does:
   * 1. **Focuses on elements our system manages:** It only pays attention to changes involving elements with the `data-uid` attribute.
   * 2. **Ignores text changes:** It skips changes to the text *inside* elements, as those aren't relevant to our system's core functionality.
   * 3. **Tracks structural changes:** It detects when "Lively" elements (those with `data-uid`) are added or removed from the page.
   * 4. **Tracks attribute changes:** It detects when specific attributes (defined in `this.LIVELY_ATTRS`) are changed on "Lively" elements.
   *
   * @param {MutationRecord} mutation - A description of a single change to the webpage.
   * @returns {{relevant: boolean, reason: string}} - An object indicating whether the change is relevant to our system and, if so, why.
   */
  isRelevantSysMutation(mutation) {
    // **Step 1: Check the type of change.**
    // We only care about changes that affect the structure of the page ("childList") or the attributes of elements.
    // Changes to text content ("characterData") are ignored.
    if (!["childList", "attributes"].includes(mutation.type)) {
      return { relevant: false, reason: "Irrelevant change type (not childList or attributes)." };
    }
  
    // **Step 2: Handle attribute changes.**
    if (mutation.type === "attributes") {
      const target = mutation.target; // The element whose attribute changed.
  
      // **Step 2a: Check if the element is a "Lively" element and if the changed attribute is one we're interested in.**
      if (target?.nodeType === 1 &&  // Make sure it's an actual element (not a text node, etc.)
          target.hasAttribute("data-uid") && // Make sure it has the "data-uid" attribute (is a Lively element)
          this.LIVELY_ATTRS.includes(mutation.attributeName)) { // Make sure the changed attribute is in our list of tracked attributes
  
        return {
          relevant: true,
          reason: `Attribute "${mutation.attributeName}" was changed on a Lively element.`,
          //Consider make the reason more descriptive by including the old and new values of the attribute.
        };
      }
      return { relevant: false, reason: "Irrelevant attribute change (not a Lively element or untracked attribute)." };
    }
  
    // **Step 3: Handle changes to the page's structure (adding or removing elements).**
    if (mutation.type === "childList") {
      // **Step 3a: Check if any elements were added that are "Lively" elements.**
      const addedRelevant = Array.from(mutation.addedNodes)
        .filter(node => node.nodeType === 1 &&  // Make sure it's an actual element
                        node.hasAttribute?.("data-uid")); // Make sure it has the "data-uid" attribute
  
      // **Step 3b: Check if any elements were removed that are "Lively" elements.**
      const removedRelevant = Array.from(mutation.removedNodes)
        .filter(node => node.nodeType === 1 && // Make sure it's an actual element
                        node.hasAttribute?.("data-uid")); // Make sure it has the "data-uid" attribute
  
      // **Step 3c: If no Lively elements were added or removed, this change is irrelevant.**
      if (addedRelevant.length === 0 && removedRelevant.length === 0) {
        return { relevant: false, reason: "Irrelevant DOM change (no Lively elements added or removed)." };
      }
  
      // **Step 3d: Create a description of what happened.**
      const details = [];
      if (addedRelevant.length > 0) {
        details.push(`${addedRelevant.length} Lively element(s) added`);
      }
      if (removedRelevant.length > 0) {
        details.push(`${removedRelevant.length} Lively element(s) removed`);
      }
  
      // **Step 3e: This change is relevant because Lively elements were added or removed.**
      return {
        relevant: true,
        reason: `DOM structure changed: ${details.join(", ")}`,
        //Consider adding more details about where the elements were added or removed.
      };
    }
  
    // If we get here, something unexpected happened.
    return { relevant: false, reason: "Unknown mutation type." };
  }
}

/**
 * DOMPatcher is responsible for applying virtual DOM patches to the real DOM.
 * It handles efficient updates such as replacing nodes, inserting children,
 * updating properties, styles, and binding/unbinding events as needed.
 */
class DOMPatcher {
  constructor(buildUidMap = true) {
    /**
     * Batch updates to be applied during the next animation frame.
     * This helps to improve performance by reducing the number of DOM mutations.
     * @type {Array<Function>}
     */
    this.batchUpdates = [];
    this.isBatching = false;
    this.patchInProgress = false;
    
    /**
     * Map of UIDs to their corresponding DOM elements.
     * @type {Map<string, HTMLElement>}
     */
    this.uidMap = new Map();
    
    if (buildUidMap) {
      this.buildUidMap(document);
    }
    
    // Monitor external DOM changes
    const debug = window?.LIVELY_APPLICATION?.DEBUG || window?.LIVELY_DEBUG || true;
    
    if (debug) {
      // Only monitor in debug mode.
      this.domObserver = new DOMObserver(this);
      this.domObserver.observe();
    }
  }
  
  /**
   * Registers a DOM element under a UID and initializes its cached props and styles.
   * 
   * This caches the element's current attributes and inline styles as plain JavaScript objects
   * for efficient diffing and patching. The cached props and styles are attached as non-standard
   * properties (`__duckCachedProps`, `__duckCachedStyle`) on the element.
   *
   * @param {string} uid - The unique identifier for the element.
   * @param {HTMLElement} el - The DOM element to register.
   * @throws {ElementRegistrationError} - Thrown when element with provided UID already exists. 
   *   Take this time to cleanup element and unregister before re-registering.
   */
  registerElement(uid, el) {
    if (this.uidMap.has(uid)) {
      throw new ElementRegistrationError("Element with the provided UID already exists. Cleanup and unregister this element first.");
    }
    this.uidMap.set(uid, el);
    this.ensureElementCacheDataInitialized(el);
  }

  /**
   * Unregisters a DOM element with a UID from the map.
   * @param {string} uid UID of the element
   */
  unregisterElement(uid) {
    this.uidMap.delete(uid);
  }

  /**
   * Gets a DOM element by its UID from the map.
   * @param {string} uid UID of the element
   * @returns {HTMLElement|null} DOM element or null if not found
   */
  getElement(uid) {
    return this.uidMap.get(uid);    
  }
  
  /**
   * Ensures Duck's cached props and style for an element are initialized to reflect the current DOM state,
   * but only for attributes and style properties that are NOT built-in (i.e., not present on a fresh tag element).
   *
   * - On first patch or event binding, call this BEFORE any mutation.
   * - After initialization, duckCachedProps will contain only Duck-relevant attributes,
   *   and duckCachedStyle will contain only Duck-relevant inline style properties.
   * - If the element's cache is already present, this is a no-op.
   *
   * @param {HTMLElement} el - The DOM element to initialize cache for.
   */
  ensureElementCacheDataInitialized(el) {
    // Exclude style from the managed props to avoid removing it if not in received props.
    // Don't keep track of `xmlns`, might be default attribute on SVG elems. 
    const propsExcludes = ["style", "xlmns"];
    const styleExcludes = [];
    
    // Initialize props cache if missing
    if (el && !el.__duckCachedProps) {
      const cachedProps = {};
      for (const attr of el.attributes) {
        if (propsExcludes.includes(attr.name)) continue;
        if (attr.name.startsWith("_")) continue; // Don't include private attributes.
        cachedProps[attr.name] = attr.value;
      }
      this.setElementCachedProps(el, cachedProps);
    }
    
    // Initialize style cache if missing
    if (el && !el.__duckCachedStyle) {
      const cachedStyle = {};
      // Only inline styles, use el.style
      for (let i = 0; i < el.style.length; i++) {
        const name = el.style[i];
        if (styleExcludes.includes(name)) continue;
        if (name.startsWith("_")) continue; // Don't include private style properties.
        cachedStyle[name] = el.style.getPropertyValue(name);
      }
      this.setElementCachedStyle(el, cachedStyle);
    }
  }

  /**
   * Retrieves the cached props (props we manage) associated with a DOM element.
   * If none exist, returns an empty object.
   *
   * Cached props are a record of the attributes previously set by this patching system,
   * rather than a snapshot of all current DOM attributes. This avoids interfering with
   * built-in or externally managed attributes.
   *
   * @param {HTMLElement} el - The DOM element whose cached props to retrieve.
   * @returns {Object} The cached props object, or {} if not present.
   */
  getElementCachedProps(el) {
    return el.__duckCachedProps || {};
  }
  
  /**
   * Sets the cached props (props we manage) on a DOM element.
   * This should be called immediately after updating the element's props via your patching system.
   *
   * Only the props explicitly set by your patching logic should be cached—never built-in, externally managed,
   * or untracked attributes. This ensures future diffing and prop removal only affects attributes managed
   * by your system, and leaves all others untouched.
   *
   * @param {HTMLElement} el - The DOM element to cache props on.
   * @param {Object} props - The props object to cache.
   */
  setElementCachedProps(el, props) {
    el.__duckCachedProps = { ...props };
  }
  
  /**
   * Retrieves the cached style (style we manage) object associated with a DOM element.
   * If none exist, returns an empty object.
   *
   * Cached style is a record of the inline style properties previously set by this patching system,
   * allowing updates and removals to only affect managed styles and not interfere with externally set styles.
   *
   * @param {HTMLElement} el - The DOM element whose cached style to retrieve.
   * @param {Boolean} latest - Whether to retrieve the latest element style attributes.
   * @returns {Object} The cached style object, or {} if not present.
   */
  getElementCachedStyle(el, latest=false) {
    if (latest) {
      const latestStyle = {};
      const styleExcludes = [];
      
      // Only inline styles, use el.style
      for (let i = 0; i < el.style.length; i++) {
        const name = el.style[i];
        if (styleExcludes.includes(name)) continue;
        if (name.startsWith("_")) continue; // Don't include private style properties.
        latestStyle[name] = el.style.getPropertyValue(name);
      }
      return latestStyle;
    }
    return el.__duckCachedStyle || {};
  }
  
  /**
   * Sets the cached style (style we manage) object on a DOM element.
   * This should be called immediately after updating the element's style via your patching system.
   *
   * Only style properties explicitly set by your patching logic should be cached. This ensures future
   * style diffing and removal only affects styles managed by your system, and preserves all other style properties.
   *
   * @param {HTMLElement} el - The DOM element to cache style on.
   * @param {Object} style - The style object to cache.
   */
  setElementCachedStyle(el, style) {
    el.__duckCachedStyle = { ...style };
  }
    
  /**
   * Builds or rebuilds a map of UIDs to their corresponding DOM elements.
   * @param {HTMLElement} rootElement Root element to build the map from
   */
  buildUidMap(rootElement) {
    const elements = rootElement.querySelectorAll('[data-uid]');
    
    // Clear UID Map.
    this.uidMap.clear();
    
    // Add elements to UID map.
    elements.forEach((el) => {
      const uid = el.dataset.uid;
      const events = (el.dataset.events || "").split(',');
      
      // Register element to UID Map.
      this.registerElement(uid, el);
      
      // Bind elements
      if (events) this.bindEvents(el, uid, events);
    });
    
    // Bind document specific events
    const pageUid = window?.PAGE_UID || window?.LIVELY_APPLICATION?.PAGE_UID || null;
    this.autobindDocumentEvents(pageUid, true);
  }
  
  /**
   * Adds a function to the batch of updates to be applied during the next animation frame.
   * Ensures that batching is non-blocking and updates run synchronously per frame for optimal UI responsiveness.
   * @param {function} fn - The function to be added to the batch of updates.
   */
  scheduleUpdate(fn) {
    // Add the function to the batch of updates
    this.batchUpdates.push(fn);

    // If batching is not already in progress, schedule the updates to be applied during the next animation frame
    if (!this.isBatching) {
      this.isBatching = true;

      requestAnimationFrame(() => {
        // Apply each update in the batch in order, allowing async if needed
        const updates = this.batchUpdates.slice();
        this.batchUpdates.length = 0;
        this.isBatching = false;

        (async () => {
          this.patchInProgress = true;
          if (this.domObserver) {
            // Skip pending mutations
            this.domObserver.observer.takeRecords();
          }
          try {
            for (const updateFn of updates) {
              // Async support for smoother UI
              if (updateFn.constructor.name === "AsyncFunction") await updateFn();
              else updateFn();
            }
          }
          finally {
            // Wait for a short delay
            await new Promise(resolve => setTimeout(resolve, 0));
            this.patchInProgress = false;
          }
        })();
      });
    }
  }
  
  /**
    * Returns true if an element can be visible in the DOM.
    */
  isVisualElement(element) {
    if (!element || !element.tagName) return false;
    
    // List of tags that are never visual in the DOM
    const nonVisualTags = [
      'SCRIPT', 'STYLE', 'META', 'TITLE', 'HEAD', 'LINK',
      'NOSCRIPT', 'BASE', 'PARAM', 'SOURCE', 'TRACK',
      'HTML',
    ];
  
    // Optionally, more tags can be added as needed
    return !nonVisualTags.includes(element.tagName.toUpperCase());
  }

  /**
   * Animates an element entering, returns a Promise resolved after animation.
   * Uses robust cleanup and supports duration override.
   * @param {HTMLElement} el - Element to animate in.
   * @param {number} duration - Duration of animation (ms). Defaults to 10 ms.
   * @param {string} animClass - Animation class to apply (default "patch-fade-in").
   * @returns {Promise<void>}
   */
  async animateIn(el, duration = 10, animClass = "patch-fade-in") {
    return new Promise(resolve => {
      function handleAnimationEnd() {
        el.classList.remove(animClass);
        if (duration) el.style.animationDuration = "";
        el.removeEventListener('animationend', handleAnimationEnd);
        resolve();
      }
      if (!this.isVisualElement(el)) return;
      if (duration) el.style.animationDuration = `${duration}ms`;
      el.classList.add(animClass);
      el.addEventListener('animationend', handleAnimationEnd, { once: true });
    });
  }

  /**
   * Animates an element exiting, returns a Promise resolved after animation.
   * Uses robust cleanup and supports duration override.
   * @param {HTMLElement} el - Element to animate out.
   * @param {number} duration - Duration of animation (ms). Defaults to 10 for default duration.
   * @param {string} animClass - Animation class to apply (default "patch-fade-out").
   * @returns {Promise<void>}
   */
  async animateOut(el, duration = 10, animClass = "patch-fade-out") {
    return new Promise(resolve => {
      function handleAnimationEnd() {
        el.classList.remove(animClass);
        if (duration) el.style.animationDuration = "";
        el.removeEventListener('animationend', handleAnimationEnd);
        resolve();
      }
      if (!this.isVisualElement(el)) return;
      if (duration) el.style.animationDuration = `${duration}ms`;
      el.classList.add(animClass);
      el.addEventListener('animationend', handleAnimationEnd, { once: true });
    });
  }
  
  /**
   * Converts a kebab-case string (e.g., "font-size") to camelCase (e.g., "fontSize").
   * Handles multiple dashes and ignores leading/trailing dashes.
   * @param {string} str The kebab-case string.
   * @returns {string} The camelCase version of the string.
   */
  toCamelCase(str) {
    return str.replace(/-([a-z])/g, (_, char) => char.toUpperCase());
  }
  
  /**
   * Converts all keys of an object from kebab-case (e.g., "font-size") to camelCase (e.g., "fontSize").
   * Leaves values unchanged.
   * @param {Object} obj The object with kebab-case keys.
   * @returns {Object} A new object with camelCased keys.
   */
  toCamelCasedObject(obj) {
    if (!obj || typeof obj !== "object") return {};
    const result = {};
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        result[toCamelCase(key)] = obj[key];
      }
    }
    return result;
  }
  
  /**
   * Apply a list of patch instructions asynchronously for responsiveness.
   * Large patch sets are chunked to avoid blocking.
   * 'await new Promise(requestAnimationFrame)' yields to the browser to keep UI smooth.
   * @param {Array} patches
   * @param {boolean} [animatePatches=False] Whether to animate patches.
   * @param {number} [chunkSize=100]
   * @returns {Promise<void>}
   */
  async applyPatches(patches, animatePatches = false, chunkSize = 100) {
    for (let i = 0; i < patches.length; i += chunkSize) {
      for (let j = i; j < Math.min(i + chunkSize, patches.length); j++) {
        this.applySinglePatch(patches[j], animatePatches);
      }
    }
  }

  /**
   * Applies a single patch instruction.
   * All DOM manipulation is batched for optimal performance.
   * @param {Array} patch
   * @param {boolean} [animatePatch=false] Whether to animate patch.
   */
  applySinglePatch(patch, animatePatch = false) {
    const [opcode, uid, payload] = patch;
    const el = this.getElement(uid); // get element from UID map
    
    switch (opcode) {
      case PatchCodes.INSERT_NODE: {
        // Insert new element to the DOM.
        if (el) {
          const [index, nodePayload] = payload;
          const child = this.buildElementDom(nodePayload, true);
          const documentFragment = document.createDocumentFragment();
          
          // Add child to fragment.
          documentFragment.appendChild(child);
          
          this.scheduleUpdate(() => {
            // Animate incoming child before insertion for smoother effect
            if (animatePatch) this.animateIn(child, 300);
            if (index >= el.childNodes.length) {
              el.appendChild(documentFragment);
            }
            else {
              el.insertBefore(documentFragment, el.childNodes[index]);
            }
            if (animatePatch) this.animateIn(child);
          });
        }
        break;
      }
      
      case PatchCodes.REPLACE_NODE: {
        // Build replacement element but don't add to UID Map immediately
        const newEl = this.buildElementDom(payload, false);
        
        if (el && el.parentNode) {
          this.scheduleUpdate(() => {
            if (!el.parentNode) return;
            // Cleanup old element, meaning its old events so that they wont be passed to newEl
            // and newEl will have its own new events.
            // This avoids ElementRegistrationError.
            this.cleanupElement(el, uid, true);
            
            // Animate outgoing element
            if (animatePatch) this.animateOut(el);
            el.parentNode.replaceChild(newEl, el);
            
            // Animate incoming element
            if (animatePatch) this.animateIn(newEl, 400)
            
            // Finally, register new element.
            this.registerElement(uid, newEl);
          });
        }
        break;
      }
      
      case PatchCodes.REMOVE_NODE: {
        // Remove an element from the DOM.
        if (el && el.parentNode) {
          this.scheduleUpdate(() => {
            if (!el.parentNode) return;
            if (animatePatch) this.animateOut(el);
            el.parentNode.removeChild(el);
            this.cleanupElement(el, uid, true);
          });
        }
        break;
      }
      
      case PatchCodes.ALTER_TEXT: {
        if (el) {
          this.scheduleUpdate(() => {
            if (animatePatch) this.animateIn(el, 300);
            this.setElementTextOrHtml(el, payload);
            if (animatePatch) this.animateIn(el);
          });
        }
        break;
      }

      case PatchCodes.REPLACE_PROPS: {
        if (el) {
          const cachedProps = this.getElementCachedProps(el);
          const newProps = payload;
          const currentEvents = (cachedProps["data-events"] || "").split(',').filter(Boolean);
          const newEvents = (newProps["data-events"] || "").split(',').filter(Boolean);
          const currentUid = (cachedProps["data-uid"] || "").trim();
          const newUid = (newProps["data-uid"] || "").trim();
          
          if (currentUid !== newUid) {
            // Register the new Uid for the element.
            // Cleanup old element before adding new one.
            // This avoids ElementRegistrationError.
            this.unregisterElement(currentUid);
            this.registerElement(newUid, el);
          }
           
          this.scheduleUpdate(() => {
            // Animate property changes for visibility
            if (animatePatch) this.animateIn(el);
            
            // Remove old props not in newProps
            for (const key in cachedProps) {
              if (!Object.prototype.hasOwnProperty.call(newProps, key)) {
                el.removeAttribute(key);
              }
            }
            
            // Add/update new props
            for (const key in newProps) {
              if (el.getAttribute(key) !== String(newProps[key])) {
                el.setAttribute(key, newProps[key]);
              }
            }
            // Unbind events no longer present
            for (const eventName of currentEvents) {
              if (!newEvents.includes(eventName)) {
                this.unbindEvents(el, [eventName]);
              }
            }
            // Bind new events not previously present
            for (const eventName of newEvents) {
              if (!currentEvents.includes(eventName)) {
                this.bindEvents(el, uid, [eventName]);
              }
            }
            // Update the cached props for future diffs
            this.setElementCachedProps(el, newProps);
          });
        }
        break;
      }

      case PatchCodes.REPLACE_STYLE: {
        if (el) {
          // For style, lets use cachedStyle.
          const cachedStyle = this.getElementCachedStyle(el, false); // Parsing 2nd arg means latest=true, meaning latest style will be fetched.
          const newStyle = payload;
          
          this.scheduleUpdate(() => {
            // Animate style changes for visibility
            if (animatePatch) this.animateIn(el);
            
            // Remove style keys not present in newStyle
            for (const styleKey in cachedStyle) {
              if (!Object.prototype.hasOwnProperty.call(newStyle, styleKey)) {
                // When setting style, we use camelCased style keys
                const camelCasedStyleKey = this.toCamelCase(styleKey);
                el.style[camelCasedStyleKey] = ""; // Remove this style property
              }
            }
            // Add/update style keys from newStyle
            for (const styleKey in newStyle) {
              // When setting style, we use camelCased style keys
              const camelCasedStyleKey = this.toCamelCase(styleKey);  
              if (el.style[camelCasedStyleKey] !== String(newStyle[styleKey])) {
                el.style[camelCasedStyleKey] = newStyle[styleKey];
              }
            }
            
            // Update the cached style for future diffs
            this.setElementCachedStyle(el, newStyle);
          });
        }
        break;
      }

      default:
        if (window.LIVELY_APPLICATION?.DEBUG) {
          console.warn(`[Lively] Unknown patch opcode: ${opcode}`);
        }
    }
  }

 /**
   * Sets an element textContent or innerHTML depending on text provided.
   * Uses regex to check for HTML tags or HTML entities.
   * @param {HTMLElement} el The target element.
   * @param {string} text The raw or markup text.
   */
  setElementTextOrHtml(el, text) {
    if (typeof text !== "string") {
      el.textContent = text == null ? "" : String(text);
      return;
    }
    
   // Check for HTML tags OR HTML entities.
    const hasHtmlTag = /<[a-z][\s\S]*>/i.test(text.trim());
    const hasHtmlEntity = /&[a-zA-Z0-9#]+;/.test(text);
    
    if (hasHtmlTag || hasHtmlEntity) {
      el.innerHTML = text;
    } else {
      el.textContent = text;
    }
  }
  
  /**
   * Recursively builds a DOM element from virtual DOM node.
   * @param {Array} node Virtual DOM node
   * @param {boolean} addToUidMap Whether to add element to UID Map.
   * @returns {HTMLElement} DOM element
   */
  buildElementDom(node, addToUidMap=true) {
    const tag = node[0];
    const uid = node[1];
    const props = node[2];
    const style = node[3];
    const text = node[4];
    const children = node[5];
    
    // Create element.
    const el = document.createElement(tag);
    
    if (uid) {
      // Assign element UID.
      el.dataset.uid = uid;
      
      // Add element to UID Map.
      if (addToUidMap) {
        const oldEl = this.getElement(uid);
        
        if (oldEl) {
          // Cleanup old element before adding new one.
          // This avoids ElementRegistrationError.
          this.unregisterElement(uid);
        }
        this.registerElement(uid, el);
      }
    }
    
    if (text) {
      // Set the innerHTML or textContent
      this.setElementTextOrHtml(el, text);
    }
    
    if (props) {
      // Set attributes
      for (const key in props) {
        if (props.hasOwnProperty(key)) {
          el.setAttribute(key, props[key]);
        } 
      }
      
      // Bind events.
      const events = props["data-events"];
      
      if (events && uid) {
        const eventTypes = events.trim().split(",");
        this.bindEvents(el, uid, eventTypes); // bind events.
      }
      
      // Set new cached props
      this.setElementCachedProps(el, props);
    }
    
    if (style) {
      // Set style for the element.
      for (const styleKey in style) {
        // Add styleKey as camelCased according to JS API
        const camelCasedStyleKey = this.toCamelCase(styleKey);
        el.style[camelCasedStyleKey] = style[styleKey];
      }
      
      // Set new cached style
      this.setElementCachedStyle(el, style);
    }
    
    // Build and add children to DOM also.
    for (const index in children) {
      el.appendChild(this.buildElementDom(children[index], true));
    }
    
    // Finally return the newly created element.
    return el;
  }
  
  /**
   * Binds client-side event listeners to the given element.
   * Stores event handlers internally to allow proper unbinding later.
   * 
   * @param {HTMLElement} el - Element to bind events to.
   * @param {string} uid - Unique identifier of the element.
   * @param {string[]} events - Array of event types to bind (e.g. ['click', 'input']).
   */
  bindEvents(el, uid, events) {
    if (!el || !events || !Array.isArray(events)) return;
    
    // Set eventHandlers Map if not set.
    if (!el._eventHandlers) el._eventHandlers = new Map();
    
    for (const i in events) {
      const eventType = events[i];
      const cleanEvent = eventType.trim();
      
      if (!cleanEvent) {
        continue;
      }
      
      const handler = async (e) => {
        const isDocumentSpecificEvent = false;
        
        if (e.type === "submit" && e.target.tagName.toUpperCase() === "FORM") {
          e.preventDefault(); // Always Prevent default on form submission.      
        }
        
        // Check element validity
        if (!(el.dataset.validate === false) && typeof el.checkValidity === "function" && typeof el.reportValidity === "function") {
          if (!el.checkValidity()) {
            el.reportValidity();
            return false;
          }
        }
        
        try {
          window.LIVELY_APPLICATION.websocketClient.sendData([
            EventOpCodes.DISPATCH_COMPONENT_EVENT,
            window.LIVELY_APPLICATION.PAGE_UID,
            uid,
            cleanEvent,
            this.extractValue(e),
            isDocumentSpecificEvent,
          ]);
        }
        catch (err) {
          if (window.LIVELY_APPLICATION.DEBUG) {
            console.error(`Error dispatching event ${cleanEvent}:`, err);
          }
        }
      };
      
      // Add event to eventHandlers map & bind element to event.
      el._eventHandlers.set(cleanEvent, handler);
      el.addEventListener(cleanEvent, handler);
    }
  }
  
  /**
   * Unbinds client-side event listeners from the given element.
   * Relies on stored event handlers for proper removal.
   * 
   * @param {HTMLElement} el - Element to unbind events from.
   * @param {string[]} events - Array of event types to unbind (e.g. ['click', 'input'] or ['onclick']).
   */
  unbindEvents(el, events) {
    if (!el || !events || !Array.isArray(events) || !el._eventHandlers) return;
  
    for (const i in events) {
      const eventType = events[i];
      const cleanEvent = eventType.trim();
      
      if (!cleanEvent) {
        continue;
      }
      
      const handler = el._eventHandlers.get(cleanEvent);
      if (handler) {
        el.removeEventListener(cleanEvent, handler);
        el._eventHandlers.delete(cleanEvent);
      }
    }
  
    if (el._eventHandlers.size === 0) {
      delete el._eventHandlers;
    }
  }
  
  /**
    * Auto bind document level events.
    * @param {string} pageUid - The current page UID. If null, it will be resolved from window.LIVELY_APPLICATION.PAGE_UID;
    * @throws LivelyError - If the pageUid is not provided and could not be resolved automatically.
    */
  autobindDocumentEvents(pageUid, dispatchDOMContentLoadedHandler = false) {
    if (!pageUid) {
      pageUid = window?.LIVELY_APPLICATION?.PAGE_UID || null;
    }
    
    // Raise an exception if pageUid is null.
    if (!pageUid) throw new LivelyError("Page UID is null and could not be resolved from window.LIVELY_APPLICATION.PAGE_UID");
    
    const pageEl = this.getElement(pageUid);
    const documentEvents = (pageEl.dataset.documentEvents || "").split(',');
    
    // Finally bind document events.
    if (documentEvents) {
      this.bindDocumentEvents(pageUid, documentEvents);
    }
  }
    
  /**
   * Binds event listeners on document for a given component UID.
   * Stores handler functions for easy removal.
   * Best: Only keep events for the current UID.
   */
  bindDocumentEvents(uid, events) {
    if (!uid || !events || !Array.isArray(events)) return;
    
    // Use a Map for handler registry
    if (!document._documentEventHandlers)
      document._documentEventHandlers = new Map();
  
    if (!document._documentEventHandlers.has(uid))
      document._documentEventHandlers.set(uid, new Map());
   
    // Retrieve handler map
    const handlerMap = document._documentEventHandlers.get(uid);
    
    for (const eventType of events) {
      const cleanEvent = eventType.trim();
      if (!cleanEvent) continue;
  
      const handler = (e) => {
        const currentUid = window.LIVELY_APPLICATION.PAGE_UID;
        const currentEventMap = document?._documentEventHandlers?.get(currentUid) || null;
        let mustDispatchEvent = false;
        
        // Only process events for current UID.
        if (!currentEventMap) return;
        for (const [eventType, eventHandler] of currentEventMap.entries()) {
          if (eventType == e.type && eventHandler ===  handler) {
            mustDispatchEvent = true;
          }
        }
        
        if (!mustDispatchEvent) {
          // Unbind this very event.
          document.removeEventListener(e.type, handler);
        }
        
        try {
          window.LIVELY_APPLICATION.websocketClient.sendData([
            EventOpCodes.DISPATCH_COMPONENT_EVENT,
            currentUid,
            currentUid,
            cleanEvent,
            this.extractValue(e),
            true, // isDocumentSpecificEvent
          ]);
        }
        catch (err) {
          if (window.LIVELY_APPLICATION.DEBUG || window.LIVELY_DEBUG) {
            console.error(`Error dispatching document event ${cleanEvent}:`, err);
          }
        }
      };
  
      // Store and bind
      handlerMap.set(cleanEvent, handler);
      document.addEventListener(cleanEvent, handler);
    }
  }
  
  /**
   * Unbinds document event listeners for a UID.
   * Call on navigation away/unmount.
   */
  unbindDocumentEvents(uid, events) {
    if (!uid || !events || !Array.isArray(events) || !document._documentEventHandlers) return;
  
    const handlerMap = document._documentEventHandlers.get(uid);
    if (!handlerMap) return;
  
    for (const eventType of events) {
      const cleanEvent = eventType.trim();
      if (!cleanEvent) continue;
  
      const handler = handlerMap.get(cleanEvent);
      if (handler) {
        document.removeEventListener(cleanEvent, handler);
        handlerMap.delete(cleanEvent);
      }
    }
  
    if (handlerMap.size === 0) {
      document._documentEventHandlers.delete(uid);
    }
    if (document._documentEventHandlers.size === 0) {
      delete document._documentEventHandlers;
    }
  }
  
  /**
   * Utility: Unbind all document events for the given UID.
   */
  unbindNonCurrentDocumentEvents(oldUid) {
    if (!document._documentEventHandlers) return;
    if (!oldUid) {
      throw new LivelyError("The provided oldUid is null or undefined.");
    }
    const handlerMap = document._documentEventHandlers.get(oldUid);
    if (!handlerMap) return;
    
    for (const [eventType, handler] of handlerMap.entries()) {
        document.removeEventListener(eventType, handler);
        document._documentEventHandlers.delete(oldUid);
    }
  }

 /**
   * Cleans up an html element before it's disposed esp when REMOVE_NODE patch is received.
   * @param {HTMLElement} el Element to bind event to
   * @param {string} uid UID of element
   * @param {boolean} removeFromUidMap Whether to remove element from UID Map.
   */
  cleanupElement(el, uid, removeFromUidMap = true) {
    const cachedProps = this.getElementCachedProps(el);
    const oldEvents = (cachedProps["data-events"] || "").split(",").filter(Boolean);
    const oldDocumentEvents = (cachedProps["data-document-events"] || "").split(",").filter(Boolean);
    
    // Unbind element events.
    if (oldEvents) this.unbindEvents(el, oldEvents);
    if (oldDocumentEvents) this.unbindDocumentEvents(uid, oldDocumentEvents);
    
    if (removeFromUidMap) {
      this.unregisterElement(uid);
    }
  }
  
  /**
   * Extracts value(s) from an event target: input, form, or custom events.
   * Returns only JSON-serializable and MessagePack-safe data for server transmission.
   * 
   * @param {Event} e - Event object.
   * @returns {any} Value(s) of the element, form data object, custom event detail, or null.
   */
  extractValue(e) {
    // Handle custom DuckNavigated event
    if (e.type === "DuckNavigated") return e.detail?.fullpath || null;
  
    const t = e.target;
  
    // Handle form elements
    if (t instanceof HTMLFormElement) {
      const data = {};
      const formData = new FormData(t);
      for (const [key, value] of formData.entries()) {
        // Ignore File objects -- send metadata only
        let safeValue = value;
        if (value instanceof File) {
          safeValue = {
            name: value.name,
            size: value.size,
            type: value.type
          };
        }
        // Support multiple values (e.g., checkboxes)
        if (data.hasOwnProperty(key)) {
          if (Array.isArray(data[key])) {
            data[key].push(safeValue);
          } else {
            data[key] = [data[key], safeValue];
          }
        } else {
          data[key] = safeValue;
        }
      }
      return data;
    }
  
    // Handle input, select, textarea, etc.
    if (t && typeof t.value !== "undefined") {
      // For checkbox, return checked state or value(s)
      if (t.type === "checkbox") {
        if (t.name && t.form) {
          const form = t.form;
          const elements = Array.from(form.elements[t.name]);
          const values = elements.filter(el => el.checked).map(el => el.value);
          return values.length > 1 ? values : (values[0] || false);
        }
        return t.checked;
      }
      // For radio, return checked value
      if (t.type === "radio") {
        if (t.name && t.form) {
          const checked = Array.from(t.form.elements[t.name]).find(el => el.checked);
          return checked ? checked.value : null;
        }
        return t.checked ? t.value : null;
      }
      // For file input, return array of metadata
      if (t.type === "file") {
        if (t.files && t.files.length) {
          return Array.from(t.files).map(f => ({
            name: f.name,
            size: f.size,
            type: f.type
          }));
        }
        return [];
      }
      // For select-multiple, return array of selected values
      if (t.tagName === "SELECT" && t.multiple) {
        return Array.from(t.selectedOptions).map(o => o.value);
      }
      // Fallback to value (string)
      return t.value;
    }
    return null;
  }
}

/**
 * Executes JavaScript and sends result over WebSocket.
 */
class JSExecutor {
  /**
   * Executes JavaScript code asynchronously with timeout.
   * If a variable is specified, its value is evaluated after code execution.
   * Feedback is only sent if execution completes within the timeout.
   *
   * @param {string} code - JavaScript code to execute.
   * @param {string|null} variable - Variable expression to extract result from.
   * @param {number|null} timeout - Timeout in milliseconds (null means no timeout).
   * @param {boolean} needsFeedback - Whether to send result/error feedback.
   * @param {string} uid - Unique identifier for the execution.
   */
  static async execute(code, variable, timeout, needsFeedback, uid) {
    let result = null;
    let error = null;
    let completed = false;

    const runEval = async () => {
      try {
        // Evaluate code
        await eval(code);
        
        if (variable) {
          result = await eval(variable);
        }
        
        // Set the completion to true.
        completed = true;
      }
      catch (err) {
        error = err.toString();
        completed = true;
        if (window.LIVELY_APPLICATION.DEBUG) {
          console.warn("[Lively] Got an error whilst executing code:");
          console.error(err);
        }
      }
    };

    // Wrap the eval task and race it against a timeout
    if (typeof timeout === "number" && timeout > 0) {
      await Promise.race([
        runEval(),
        new Promise(resolve => setTimeout(resolve, timeout))
      ]);
    }
    else {
      await runEval();
    }

    // Only send feedback if eval completed and needsFeedback is true
    if (needsFeedback && completed) {
      this.sendFeedback(result, error, uid);
    }
  }

  /**
   * Sends the result or error to the server over WebSocket.
   *
   * @param {*} result - The evaluated variable result.
   * @param {string|null} error - Error message, if any.
   * @param {string} uid - Execution UID.
   */
  static sendFeedback(result, error = null, uid) {
    try {
      window.LIVELY_APPLICATION.websocketClient.sendData([
        EventOpCodes.JS_EXECUTION_RESULT,
        result,
        error,
        uid,
      ]);
    }
    catch (e) {
      if (window.LIVELY_APPLICATION.DEBUG) {
        console.error("Failed to send JS execution feedback:", e);
      }
    }
  }
}


/**
 * Parses a URL into its domain and full path components.
 * @param {string} url URL to parse
 * @returns {Object} Parsed URL object with domain and fullpath properties
 */
function URL(url) {
  // Create a temporary anchor element to parse the URL
  const parser = document.createElement('a');
  
  // Set href & return result.
  parser.href = url;
  
  return {
    /**
     * Domain of the URL (e.g. example.com)
     * @type {string}
     */
    domain: parser.hostname,
    /**
     * Full path of the URL (e.g. /path/to/resource?query=param#anchor)
     * @type {string}
     */
    fullpath: parser.pathname + parser.search + parser.hash,
  };
}


/**
 * Handles navigation requests and responses.
 */
class NavigationHandler {
  /**
   * Builds up navigation headers the way browsers do.
   * @returns {Object} Navigation headers
   */
  static getNavigationHeaders() {
    // Initialize headers object with common navigation headers
    let headers = {
      /**
       * Referer header (current URL)
       * @type {string}
       */
      "Referer": window.location.href,
      /**
       * Host header (current host)
       * @type {string}
       */
      "Host": window.location.host,
      /**
       * User-Agent header (browser user agent)
       * @type {string}
       */
      "User-Agent": navigator.userAgent,
    };

    // Add Cookie header if cookies are present
    if (document.cookie) {
      headers["Cookie"] = document.cookie;
    }
    
    // Finally return headers.
    return headers;
  }
  
  /**
    * Do a full page reload.
    *
    * @param {string} url URL to navigate to.
    * @param {string} reason Reason for full reload
    */
  static doFullPageReload(url, reason) {
    if (url) {
      window.location.href = url;
    }
  }
  
  /**
    * Scroll to page top if not.
    * @param {boolean} smooth - Whether the scroll must be smooth. Defaults to false for instant scroll.
    */
  static scrollToTop(smooth = false) {
    if (window.scrollY === 0) return;
    if (smooth) window.scrollTo({ top: 0, behavior: 'smooth' });
    else window.scrollTo({ top: 0});
  }
  
  /**
   * Sends a navigation request to the WebSocket.
   * @param {string} url URL to navigate to
   * @param {string} nextPageUid The next page Uid to navigate to (if available). Useful in previous navigations. 
   */
  static navigateTo(url, nextPageUid) {
    const serverTrustedURL = window.LIVELY_WS_URL;
    const parsedUrl = URL(url || "");
    const websocket = window.LIVELY_APPLICATION.websocketClient.socket;
    const progressBar = window.LIVELY_APPLICATION.PAGE_PROGRESS_BAR;
    let progress = window.LIVELY_APPLICATION.PAGE_PROGRESS;
    
    function updateProgress() {
      // Update progress bar with transform for perf
      progress = window.LIVELY_APPLICATION.PAGE_PROGRESS = Math.min(progress + 10, 100);
      updateProgressBar(progressBar, progress); 
    }
    
    if (!this.navigationInProgress) {
      this.navigationInProgress = true;
    }
    else {
      // Navigation already in progress.
      return;
    }
    
    // Reset page progress
    window.LIVELY_APPLICATION.resetPageProgressBar();
    
    // Check if websocket open.
    if (!(websocket && websocket.readyState === WebSocket.OPEN)) {
      this.doFullPageReload(url, "WebSocket not open");
      return;
    }

    // Check if we have a valid page UID
    if (!window.LIVELY_APPLICATION.PAGE_UID) {
      // Server won't be able to do a diff with no previous uid
      this.doFullPageReload(url, "Page UID not set");
      return;
    }
    
    // Check if nextPageUid is parsed
    if (nextPageUid) {
      // Update progress bar with transform for perf
      updateProgress();
      
      // Send navigation request
      window.LIVELY_APPLICATION.websocketClient.sendData([
        EventOpCodes.NAVIGATE_TO,
        window.LIVELY_APPLICATION.PAGE_UID,
        nextPageUid,
        parsedUrl.fullpath,
        this.getNavigationHeaders(),
      ]);
      return;
    }

    // Check if the server LIVELY_WS_URL is set
    if (!serverTrustedURL) {
      // The server LIVELY_WS_URL is not set, just do a full reload to the URL
      this.doFullPageReload(url, "LIVELY_WS_URL not set");
      return;
    }
    
    // Check if the URL is a path or an absolute URL
    const serverDomain = URL(serverTrustedURL).domain;
    
    if (!parsedUrl.domain) {
      // This is a URL path, send navigation request to WebSocket
      // Update progress bar with transform for perf
      updateProgress();
      
      // Send navigation request. 
      window.LIVELY_APPLICATION.websocketClient.sendData([
        EventOpCodes.NAVIGATE_TO,
        window.LIVELY_APPLICATION.PAGE_UID,
        nextPageUid || null,
        parsedUrl.fullpath,
        this.getNavigationHeaders(),
      ]);
    }
    else {
      // This is an absolute URL
      if (serverDomain === parsedUrl.domain) {
        // This URL is directed to the right server, send navigation request
        // Update progress bar with transform for perf
        updateProgress();
        
        // Send navigation request.
        window.LIVELY_APPLICATION.websocketClient.sendData([
          EventOpCodes.NAVIGATE_TO,
          window.LIVELY_APPLICATION.PAGE_UID,
          nextPageUid || null,
          parsedUrl.fullpath,
          this.getNavigationHeaders(),
        ]);
      }
      else {
        this.doFullPageReload(url, "Parsed URL domain doesn't match that of remote lively server");
      }
    }
  }
  
  /**
   * Handles a navigation result sent by the server.
   * @param {string} fullpath Full path of the URL
   * @param {boolean} fullreload Whether to do a full reload
   * @param {string} nextPageUid Next page UID
   * @param {Array} patches Patches to apply
   * @param {boolean} isFinal Whether the sent patches are final.
   */
  static async handleResponse(fullpath, fullreload, nextPageUid, patches, isFinal) { 
    if (fullreload) {
      // This means the server is unable to provide patches for the navigation request
      // but it's asking us just to do a full reload to the urlpath
      window.LIVELY_APPLICATION.resetPageProgressBar();
      this.doFullPageReload(fullpath, "Server could not provide possible patches");
    }
    else if (this.navigationInProgress) {
      // The server has got patches for us.
      let progress = window.LIVELY_APPLICATION.PAGE_PROGRESS;
      let progressBar = window.LIVELY_APPLICATION.PAGE_PROGRESS_BAR;
      
      // Update progress bar with transform.
      progress = window.LIVELY_APPLICATION.PAGE_PROGRESS = Math.min(progress + 10, 95);
      updateProgressBar(progressBar, progress);
      
      // Update the page uid
      // Unbind all previous page document-specific events.
      if (window.LIVELY_APPLICATION.PAGE_UID !== nextPageUid) {
        // The next page uid is not equal to the current one.
        const oldPageUid = window.LIVELY_APPLICATION.PAGE_UID;
        window.LIVELY_APPLICATION.patcher.unbindNonCurrentDocumentEvents(oldPageUid);
      }
      
      // Finally update page UID
      window.LIVELY_APPLICATION.PAGE_UID = nextPageUid;
      
      // Update the window history (only if allowed)
      if (!this._noPushState) {
        this.pushState(nextPageUid, fullpath);
      }

      // Reset noPushState
      this._noPushState = false;
      
      // Apply new patches
      await window.LIVELY_APPLICATION.patcher.applyPatches(patches, true);
      
      // Reinitialize progress bar if it has changed (this will get a live result for progress bar)
      progressBar = window.LIVELY_APPLICATION.PAGE_PROGRESS_BAR;
      
      // We have received all patches but we might not be done patching the DOM.
      if (isFinal) {
        const progressBarInner = progressBar.querySelector('#progress-bar-inner');
        
        // Scroll to top (if not already at top).
        this.scrollToTop();
      
        // Cancel navigation in progress flag.
        this.navigationInProgress = false;
        
        if (progress === 100) {
          // Progress already at max.
          window.LIVELY_APPLICATION.resetPageProgressBar();
          
          // Reinitialize the new page.
          reinitializePage(true);
          
          if (this.scrollCoordinates) {
              window.scrollTo(this.scrollCoordinates);
              // Reset scroll coordinates
              this.scrollCoordinates = null;
            }
          return;
        }
        
        // Listen for transition end
        function onTransitionEnd(e) {
          if (e.propertyName === 'transform') { // or 'width', depending on your CSS
            window.LIVELY_APPLICATION.resetPageProgressBar();
            progressBarInner.removeEventListener('transitionend', onTransitionEnd);
            
            // Reinitialize the new page.
            reinitializePage(true);
            
            if (this.scrollCoordinates) {
              window.scrollTo(this.scrollCoordinates);
              
              // Reset scroll coordinates
              this.scrollCoordinates = null;
            }
          }
        }
        
        // Add transition end event.
        progressBarInner.addEventListener('transitionend', onTransitionEnd);
        
        // The function updateProgressBar is defined just below every ProgressBar component.
        progress = window.LIVELY_APPLICATION.PAGE_PROGRESS = 100;
        updateProgressBar(progressBar, progress);        
      }
    }
  }
  
  /**
   * Pushes a new state into the browser history if it differs from the current state.
   *
   * This function updates the browser's history stack using `window.history.pushState`
   * only when the next page UID or the URL path differs from the current one.
   * This helps prevent unnecessary duplicate entries in the history stack,
   * avoiding redundant navigation events and potential UI re-renders.
   *
   * @param {string} nextPageUid - Unique identifier for the next page/state.
   * @param {string} fullpath - The full URL path (including pathname, query, and hash) to push.
   *
   * @returns {void} Does not return any value.
   */
  static pushState(nextPageUid, fullpath) {
    const currentState = window.history.state;
    const currentURL = window.location.pathname + window.location.search + window.location.hash;
  
    // Check if the current state or URL is the same as the new one
    if (
      currentState && currentState.pageUid === nextPageUid ||
      currentURL === fullpath
    ) {
      // Same state or same URL, no need to push again
      return;
    }
  
    // Only push if different
    window.history.pushState({ pageUid: nextPageUid }, '', fullpath);
    
    // Bind on popstate
    if (!(this._bindedOnPopState)) {
      this.bindOnPopState();
      this._bindedOnPopState = true;
    }
  }
  
  /**
   * Handles the popstate event by loading the component based on
   * the current URL path.
   * Automatically binds the popstate event listener.
   */
  static bindOnPopState() {
    window.addEventListener('popstate', (event) => {
      const fullpath = window.location.pathname + window.location.search + window.location.hash;
      
      // Set noPushState and do navigation - avoid duplicate pushstates (preventing navigating to same path 2 or more time on popstate) 
      this._noPushState = true;
      
      // Do the actual navigation
      const nextPageUid = event.state?.pageUid || window?.LIVELY_APPLICATION?.INITIAL_PAGE_UID || null;
      duckNavigate(fullpath, nextPageUid);
    });
  }
}

/**
 * WebSocket client for Lively component system.
 * Handles patch dispatching, event execution, and JS evaluation.
 */
class LivelyWebSocketClient {
  /**
   * Initialize the lively websocket client.
   * @param {string} websocketURL - URL for the WebSocket server.
   * @param {object} patcher - Object responsible for applying patches.
   */
  constructor(websocketURL, patcher) {
    this.websocketURL = websocketURL;
    this.patcher = patcher;
    this._reconnectInProgress = false;  // Flag to track if a reconnect attempt is ongoing
    this._reconnectAbortController = null; // Controller to cancel ongoing reconnect attempts
  }
  
  /**
    * Cleanup websocket connection.
    */
  cleanupSocket() {
    if (this.socket) {
      this.socket.onopen = null;
      this.socket.onerror = null;
      this.socket.onclose = null;
      this.socket.onmessage = null;
      try { this.socket.close(); } catch (e) {}
      this.socket = null;
    }
  }
    
  /**
   * Establishes WebSocket connection with given URL.
   * Starts the connection and sets up event handlers.
   */
  connect() {
    // Cleanup old socket if any
    this.cleanupSocket();
    
    // Do the real connection.
    this.socket = new WebSocket(this.websocketURL); 
    this.socket.binaryType = "arraybuffer";
    
    this.socket.onopen = () => {
      // We are now connected to the server.
      if (window.LIVELY_APPLICATION.DEBUG) {
        console.log("[Lively] WebSocket connected.");
      }
      
      if (window._initialDOMContentLoadedEventSent === undefined) {
        const pageUid = window.LIVELY_APPLICATION.PAGE_UID;
        const pageEl = this.patcher.getElement(pageUid);
        const cachedProps = this.patcher.getElementCachedProps(pageEl);
        const documentEvents = (cachedProps["data-document-events"] || "").split(",").filter(Boolean);
        
        if (documentEvents) {
          for (const event of documentEvents) {
            if (event === "DOMContentLoaded") {
              const handlerMap = document._documentEventHandlers.get(pageUid);
              for (const [eventType, eventHandler] of handlerMap.entries()) {
                if (eventType === event) {
                  eventHandler(new Event(event)); // Execute event handler
                  window._initialDOMContentLoadedEventSent = true; // Sent initial DOMContentLoaded event to server
                  break; // Break on first handler execution.
                }
              }
            }
          }
        }
      }
      
      // Show connected snackbar.
      const snackbar = window.LIVELY_APPLICATION.PAGE_SNACKBAR;
      snackbar.LABEL.textContent = "Connected"
      
      // Show a success snackbar and autohide.
      showSnackbar(snackbar, "success", 2000);
      
      // Connected, no reconnect ongoing
      this._reconnectInProgress = false;
      
      // Abort any ongoing reconnect delays
      if (this._reconnectAbortController) {
        this._reconnectAbortController.abort();
        this._reconnectAbortController = null;
      }
    };
    
    this.socket.onerror = (e) => {
      // We got some websocket error.
      if (window.LIVELY_APPLICATION.DEBUG) {
        console.error("[Lively] WebSocket error:", e);
      }
    };
    
    this.socket.onclose = async (e) => {
      // Websocket connection lost.
      if (window.LIVELY_APPLICATION.DEBUG) {
        console.warn("[Lively] WebSocket closed:", e);
      }
      
      // Reset navigation in progress flag.
      NavigationHandler.navigationInProgress = false;
      
      // Reset progressbar if present.
      window.LIVELY_APPLICATION.resetPageProgressBar();
      
      // Show not connected snackbar.
      if (!this._reconnectInProgress) {
        const snackbar = window.LIVELY_APPLICATION.PAGE_SNACKBAR;
        snackbar.LABEL.textContent = "Disconnected!"
      
        // Show an error snackbar and autohide.
       showSnackbar(snackbar, "error", 2000);
      }
      
      // Attempt reconnection on connection close.
      await this.tryReconnect();
    };

    this.socket.onmessage = async (event) => {
      // We received some binary.
      let data;
      
      // Try decoding the data.
      try {
        data = Msgpack.decode(event.data);
      }
      catch (err) {
        // Error in decoding the binary data.
        if (window.LIVELY_APPLICATION.DEBUG) {
          console.error("[Lively] Decode failed:", err);
        }
        return;
      }
      
      // Process data from the remote server.
      const opcode = data[0];
       
      if (EventOpCodes.CLIENT_EVENT_OPCODES.has(opcode)) {
        switch (opcode) {
          case EventOpCodes.APPLY_PATCH:
            // Wait for patch application to complete.
            await this.patcher.applyPatches(data[1]);
            break;
          
          case EventOpCodes.EXECUTE_JS: {
            // Execute JS on server behalf.
            const [_, code, variable, timeout, needsFeedback, uid] = data;
            JSExecutor.execute(code, variable, timeout, needsFeedback, uid);
            break;
          }

          case EventOpCodes.NAVIGATION_RESULT: {
            // Handle navigation response from server, whether apply patches or do a fullpage reload.
            const [_, fullpath, fullreload, nextPageUid, patches, isFinal] = data;
            await NavigationHandler.handleResponse(fullpath, fullreload, nextPageUid, patches, isFinal);
            break;
          }
          
          case EventOpCodes.COMPONENT_UNKNOWN: {
            // Handle the response from server
            const [_, must_reload] = data;
            const snackbar = window.LIVELY_APPLICATION.PAGE_SNACKBAR;
            
            if (must_reload) {
              // Show an info snackbar and autohide.
              snackbar.LABEL.textContent = "Session expired, reloading...";
              showSnackbar(snackbar, "warning", 2000);
              
              // Server can't provide patches if it has no reference to current component so,
              // do a fullpage reload.
              window.location.reload();
            }
            break;
          }
        }
      }
    };
  }

  /**
   * Encodes and sends payload to server if connection is open.
   * @param {*} payload - Payload to send.
   * @param {Boolean} reconnectWhenNotConnected - Whether to reconnect if not connected to the remote server.
   */
  async sendData(payload, reconnectWhenNotConnected = true) {
    // Send data asynchronously.
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const data = Msgpack.encode(payload);
      this.socket.send(data);
    }
    else {
      // Websocket is not open.
      if (window.LIVELY_APPLICATION.DEBUG) {
        console.warn("[Lively] Cannot send message: WebSocket is not open.");
      }
      
      // Reset progress bar if present.
      window.LIVELY_APPLICATION.resetPageProgressBar();
      
      // Show not connected snackbar
      const snackbar = window.LIVELY_APPLICATION.PAGE_SNACKBAR;
      snackbar.LABEL.textContent = "Not connected!"
      
      // Show an error snackbar and autohide.
      showSnackbar(snackbar, "error", 2000);
       
      if (reconnectWhenNotConnected) {
        // Attempt reconnection.
        await this.tryReconnect();
        
        // Retry sending data once after reconnect.
        await this.sendData(payload, false);
      }
    }
  }

  /**
   * Attempts to reconnect to the WebSocket with exponential backoff.
   * Prevents multiple simultaneous reconnect attempts.
   * Supports graceful cancellation of ongoing reconnect delays.
   * @param {number} delay - Initial delay in seconds before next retry.
   * @param {number} maxRetries - The maximum number of retries.
   */
  async tryReconnect(delay = 1, maxRetries = 5) {
    if (this._reconnectInProgress) {
      // Already trying to reconnect, so skip this call
      return;
    }

    this._reconnectInProgress = true;
    let retries = 0;
    let currentDelay = delay;
    this._reconnectAbortController = new AbortController();

    const sleep = (ms, signal) => new Promise((resolve, reject) => {
      const timeout = setTimeout(resolve, ms);
      signal.addEventListener('abort', () => {
        clearTimeout(timeout);
        reject(new Error('Reconnect sleep aborted'));
      });
    });

    const reconnect = async () => {
      // Only attempt reconnection if not already connected.
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this._reconnectInProgress = false; // Connected successfully
        this._reconnectAbortController = null;
        return;
      }
      
      if (retries >= maxRetries) {
        // Reconnection failed after max attempts
        if (window.LIVELY_APPLICATION.DEBUG) {
          console.warn(`[Lively] Failed to reconnect after ${maxRetries} retries`);
        }
        this._reconnectInProgress = false;
        this._reconnectAbortController = null;
        return;
      }
      
      try {
        // Attempt reconnection.
        this.connect();
        retries++;
        // Wait with exponential backoff before next retry if needed
        await sleep(currentDelay * 1000, this._reconnectAbortController.signal);
        currentDelay *= 2;
        await reconnect();
      }
      catch (e) {
        if (e.message !== 'Reconnect sleep aborted' && window.LIVELY_APPLICATION.DEBUG) {
          console.error("[Lively] Reconnect error:", e);
        }
        this._reconnectInProgress = false;
        this._reconnectAbortController = null;
      }
    };
    
    // Do the actual reconnection.
    await reconnect();
  }
}

/**
  * Main application implementation.
  */
class LivelyApp {
  /**
    * Initialize the Lively entry point.
    */
  constructor () {
    /**
     * @private
     * @type {LRUCache<string, HTMLElement>}
     * Cache to store recently fetched DOM elements by ID.
     */
    this.__cachedLiveDOMElements = new LRUCache(128);
    
    // Some metadata
    this.DEBUG = window.LIVELY_DEBUG;
    this.WS_URL = window.LIVELY_WS_URL;
    
    // Keep track of components (components that may be represent full webpage).
    this.PAGE_UID = window.PAGE_UID || null;
    this.INITIAL_PAGE_UID = this.PAGE_UID;
    
    // Define Live DOM elements (they always refetch from DOM if the cached elem ID doesn't match the initial ID)
    this.defineLiveElementProperty("PAGE_SNACKBAR", "page-snackbar");
    this.defineLiveElementProperty("PAGE_PROGRESS_BAR", "page-progress-bar");
    
    // Assign important elem specific attributes
    this.PAGE_SNACKBAR.LABEL = this.PAGE_SNACKBAR.querySelector("#snackbar-label");
    this.PAGE_PROGRESS = 0;
    
    // Do some magic
    this.duckEvents = {};
    this.createDuckEvent("DuckNavigated", {}, true); // Create custom Duck-specific event
    
    // Create some objects.
    this.patcher = new DOMPatcher();
    this.websocketClient = new LivelyWebSocketClient(this.WS_URL, this.patcher);
    
    // Override anchor navigation.
    this.overrideAnchorNavigation();
    this.initialized = true;
  }
  
  /**
   * Defines a *live* property on the current instance that automatically
   * resolves to a DOM element with a given ID. The property uses an internal
   * LRU cache to store and reuse recently fetched elements, and it will
   * transparently re-fetch from the DOM whenever the cached element is
   * missing, detached, or replaced.
   *
   * Example:
   * ```js
   * this.defineLiveElementProperty("PAGE_SNACKBAR", "page-snackbar");
   * console.log(this.PAGE_SNACKBAR); // → <div id="page-snackbar">...</div>
   * ```
   *
   * Once defined, accessing `this.PAGE_SNACKBAR` will always return the most
   * recent `<div id="page-snackbar">` element in the document, even if the
   * DOM changes dynamically.
   *
   * Setting the property manually (e.g. `this.PAGE_SNACKBAR = someElem`) will
   * override the cached reference and update the LRU cache entry.
   *
   * @param {string} propertyName - The name of the property to define on this instance.
   * @param {string} elemID - The `id` attribute of the DOM element to bind to.
   *
   * @private
   */
  defineLiveElementProperty(propertyName, elemID) {
    const self = this;
  
    Object.defineProperty(this, propertyName, {
      configurable: true,
      enumerable: true,
  
      get() {
        // Try cache first
        let cached = self.__cachedLiveDOMElements.get(elemID);
  
        // Verify the element still exists in the DOM
        if (!cached || cached.id !== elemID || !document.body.contains(cached)) {
          // Refetch from DOM
          const elem = document.getElementById(elemID);
          
          if (elem) {
            // Store in cache
            self.__cachedLiveDOMElements.set(elemID, elem);
            cached = elem;
          }
          else if (self.DEBUG) {
            console.warn(`[Lively] Element with ID '${elemID}' not found.`);
          }
        }
        return cached || null;
      },
  
      set(value) {
        // Allow manual override, but also update the cache
        if (value instanceof HTMLElement) {
          self.__cachedLiveDOMElements.set(elemID, value);
        }
        else if (self.DEBUG) {
          console.warn(`[Lively] Attempted to set ${propertyName} to a non-HTMLElement.`);
        }
      }
    });
  }

  /**
   * Prepares custom Duck-specific DOM events.
   * This utility supports future extension to multiple event types.
   *
   * Usage:
   *   const event = createDuckEvent('DuckNavigated', {
   *     fullpath: ...,
   *   });
   *   // document.dispatchEvent(event); // Dispatch when ready
   *
   * @param {string} eventName - The name of the event to create (e.g., 'DuckNavigated').
   * @param {Object} [detailOverrides] - Optional: properties to override or add to the event's detail object.
   * @param {boolean} [addToDuckEvents=true] Whether to add the created event to event list.
   * @returns {CustomEvent} The prepared CustomEvent instance.
   */
  createDuckEvent(eventName, detailOverrides = {}, addToDuckEvents = true) {
    // Gather common details
    let defaultDetails = {};
    
    if (eventName === "DuckNavigated") {
      defaultDetails = {
        fullpath: window.location.pathname + window.location.search + window.location.hash,
      };
    }
    
    // Merge overrides with defaults
    const detail = { ...defaultDetails, ...detailOverrides };
  
    // Create the event, ready to be dispatched
    const newEvent = new CustomEvent(eventName, {
      bubbles: true, // Enable event bubbling for listeners
      detail,
    });
    
    if (addToDuckEvents) this.duckEvents[eventName] = newEvent;
    return newEvent;
  }
  
  /**
    * Resets the page progress bar to zero.
    */
  resetPageProgressBar() {
    // Hide progress bar, to avoid transition.
    hideProgressBar(this.PAGE_PROGRESS_BAR);
    
    // Reset navigation progress
    this.PAGE_PROGRESS = 0;
  }
  
  /**
   * Overrides the browser's default navigation for internal <a> elements,
   * enabling Duck Framework's SPA-style routing via duckNavigate().
   *
   * - Works for normal left-clicks on same-origin links.
   * - Ignores:
   *   - External links
   *   - Links with `target="_blank"`
   *   - Links with `data-no-duck` attribute
   *   - Clicks with modifier keys (Ctrl, Shift, Meta, Alt)
   * - Falls back to normal navigation if duckNavigate is not available.
   */
  overrideAnchorNavigation() {
    document.addEventListener(
      "click",
      (event) => {
        const link = event.target.closest("a");
        if (!link || !link.href) return;

        // Respect modifier keys
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

        // Skip if it's external, opens in new tab, or disabled
        if (
          link.target === "_blank" ||
          link.origin !== location.origin ||
          link.hasAttribute("data-no-duck")
        ) return;

        // If the event was already handled (e.g., by another handler), don't run
        if (event.defaultPrevented) return;

        // Only prevent default after other listeners had a chance to run (capture phase!)
        event.preventDefault();

        const targetPath = link.pathname + link.search + link.hash;

        if (typeof duckNavigate === "function") {
          duckNavigate(targetPath);
        }
        else {
          if (this && this.DEBUG) {
            console.warn("duckNavigate() is not defined. Falling back to default navigation.");
          }
          NavigationHandler.doFullPageReload(link.href, "duckNavigate() could not be resolved");
        }
      },
      true // Use capture phase: runs before other bubble-phase listeners
    );
  }
    
  /**
    * Initialize the Lively application system.
    */
  init() {
    if (this.WS_URL) {
      try {
        // Connect to the WebSocket.
        this.websocketClient.connect();
      }
      catch (e) {
        console.error(e.toString());
        this.websocketClient.tryReconnect();
      }  
    }
    else {
      console.warn("[Lively] window.LIVELY_WS_URL is not set, yet it is required");
    }
  }
}

/**
  * Duck's navigation function which avoids fullpage reload whenever possible.
  *
  * @param {string} url The URL to navigate to.
  * @param {string} nextPageUid The next page Uid to navigate to (if available). Useful in previous navigations.
  */
function duckNavigate(url, nextPageUid) {
  NavigationHandler.navigateTo(url, nextPageUid);
}

/**
  * Duck version of window.open
  */
function windowOpen(url, target) {
 if (target != "_blank") {
  duckNavigate(url);
 }
 else {
   if (window.overridenWindowOpen) {
     window.super_open(url, target);
   }
   else {
     window.open(url, target);
   }
 }
}

/**
  * Function for overriding default window.open.
  */
function overrideWindowOpen() {
  if (!window.overridenWindowOpen) {
    window.super_open = window.open;
    window.open = windowOpen;
    window.overridenWindowOpen = true; 
  }
}


/**
  * Reinitialize the page by refiring DomContentLoaded event.
  * @param {boolean} [fireDuckNavigatedEvent=true] Whether to fire a DuckNavigated event to flag that a navigation was successful.
  */
function reinitializePage(fireDuckNavigatedEvent=true) {
  const livelyApp = window.LIVELY_APPLICATION;
  
  if (livelyApp) {
    // Automatically bind all current page document level events.
    livelyApp.patcher.autobindDocumentEvents();
  }
  
  // Fire some events.
  document.dispatchEvent(new Event('DOMContentLoaded'));
  
  if (fireDuckNavigatedEvent) {
    const duckNavigatedEvent = livelyApp.duckEvents["DuckNavigated"];
    document.dispatchEvent(duckNavigatedEvent);
  } 
}

if (!window.LIVELY_APPLICATION) {
  // Expose and initialize application
  // Only one app per client.
  window.LIVELY_SCRIPT_COMPATIBLE = true; // If no syntax errors then script is ok.
  window.addEventListener("DOMContentLoaded", () => {
    if (!window.LIVELY_APPLICATION) {
      // Avoid multiple apps here also.
      // Override window.open
      overrideWindowOpen();
      window.LIVELY_APPLICATION = new LivelyApp();
      window.LIVELY_APPLICATION.init();
    }
  }); 
}

// Set that full lively.js has been received.
window.receivedFullLivelyJs = true;

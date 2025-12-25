<template>
  <div class="app" @click="handleAppClick">
    <!-- Main map viewer -->
    <MapboxViewer
      ref="mapboxViewerRef"
      :lightingVisible="lightingVisible"
      :vibrancyVisible="vibrancyVisible"
      :combinedVisible="combinedVisible"
      :heightScale="heightScale"
      :showHubs="routingHubsVisible"
      @ready="onViewerReady"
      :focusZurichKey="zurichFocusKey"
      :fromButton="zurichFromButton"
      @zurichZoomComplete="handleZurichZoomComplete"
      @zoom="handleMapZoom"
      @move="handleMapMove"
      @mapReady="handleMapReady"
      @hubsUpdated="handleHubsUpdated"
      @routePopupClicked="handleRoutePopupClicked"
      @hubsSelected="handleHubsSelected"
      @polygonClicked="handlePolygonClicked"
      @mapClicked="handleMapClicked"
    />

    <!-- Top Center Buttons Container -->
    <div
      v-if="
        (currentRouteStats && mapZoom >= 11.5) ||
        activeLayerName ||
        routeAnimationActive ||
        routeSecurityAlertsActive
      "
      class="top-center-buttons-container"
      :class="{
        'top-center-buttons-container--zurich-message-visible':
          showZurichReturnMessage,
      }"
    >
      <!-- Clear Route Button -->
      <div
        v-if="currentRouteStats && mapZoom >= 11.5"
        class="clear-route-top-button"
      >
        <img
          src="/routing_icon.svg"
          alt="Route"
          class="clear-route-icon"
          width="16"
          height="16"
        />
        <span>Route</span>
        <button
          class="clear-route-close"
          @click.stop="handleClearRoute"
          aria-label="Clear route"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Clear Animation Button -->
      <div
        v-if="routeAnimationActive && mapZoom >= 11.5"
        class="clear-route-top-button"
      >
        <svg
          class="clear-route-icon"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polygon points="5 3 19 12 5 21 5 3" />
        </svg>
        <span>Animation</span>
        <button
          class="clear-route-close"
          @click.stop="handleResetAnimation"
          aria-label="Clear animation"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Clear Security Alerts Button -->
      <div
        v-if="routeSecurityAlertsActive && mapZoom >= 11.5"
        class="clear-route-top-button"
      >
        <svg
          class="clear-route-icon"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <path d="M12 8v4"></path>
          <path d="M12 16h.01"></path>
        </svg>
        <span>Security Alerts</span>
        <button
          class="clear-route-close"
          @click.stop="toggleRouteSecurityAlerts"
          aria-label="Clear security alerts"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Active Layer Indicator Button -->
      <div v-if="activeLayerName" class="active-layer-button">
        <svg
          class="active-layer-icon"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
        <span class="active-layer-name">{{ activeLayerName }}</span>
        <button
          class="active-layer-close"
          @click.stop="clearActiveLayer"
          aria-label="Clear layer"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Hotspot Name Pop-up -->
    <transition name="hotspot-name-fade">
      <div
        v-if="displayedHotspotName"
        class="hotspot-name-popup"
        :class="{ 'hotspot-name-popup--faded': hotspotNameFaded }"
      >
        {{ displayedHotspotName }}
      </div>
    </transition>

    <!-- Route Saved to History Message -->
    <div v-if="showRouteSavedMessage" class="route-saved-message">
      <span class="route-saved-text">Route saved to history</span>
      <div class="route-saved-actions">
        <button
          class="route-saved-button route-saved-button--close"
          @click.stop="showRouteSavedMessage = false"
        >
          Ok
        </button>
        <button
          class="route-saved-button route-saved-button--open"
          @click.stop="openHistorySection"
        >
          Open History
        </button>
      </div>
    </div>

    <!-- Go Back to Zurich Message -->
    <transition name="zurich-return-fade">
      <div v-if="showZurichReturnMessage" class="zurich-return-message">
        <span class="zurich-return-text">Go back to Zurich?</span>
        <div class="zurich-return-actions">
          <button
            class="zurich-return-button zurich-return-button--yes"
            @click.stop="handleGoBackToZurich"
          >
            Yes
          </button>
          <button
            class="zurich-return-button zurich-return-button--close"
            @click.stop="showZurichReturnMessage = false"
            aria-label="Close"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>
    </transition>

    <!-- Sidebar controls -->
    <aside
      :class="[
        'sidebar',
        {
          'sidebar--collapsed': sidebarCollapsed,
          'sidebar--highlight': sidebarHighlight,
        },
      ]"
      :style="!sidebarCollapsed ? { width: sidebarWidth + 'px' } : {}"
      @mouseenter="handleSidebarMouseEnter"
      @mouseleave="handleMouseLeave"
      @click.stop="handleSidebarClick"
    >
      <!-- Resize handle -->
      <div
        class="sidebar-resize-handle"
        @mousedown="startResize"
        @mouseenter="isResizing = true"
        @mouseleave="isResizing = false"
      ></div>
      <!-- Sidebar Icon Bar (VS Code style) -->
      <div class="sidebar-icon-bar">
        <div class="sidebar-icon-bar-top">
          <!-- Toggle button at top when collapsed, or in header when expanded -->
          <button
            v-if="sidebarCollapsed"
            class="sidebar-icon-btn sidebar-toggle-icon-btn"
            :class="{ 'sidebar-toggle--will-close': !sidebarCollapsed }"
            @click.stop="handleToggleSidebar"
            :aria-expanded="!sidebarCollapsed"
            aria-label="Toggle sidebar"
          >
            <img
              src="/sidebar.svg"
              alt="Toggle sidebar"
              class="sidebar-toggle-icon"
              aria-hidden="true"
            />
            <span class="sidebar-icon-tooltip">
              {{ sidebarCollapsed ? "Open sidebar" : "Close sidebar" }}
            </span>
          </button>

          <!-- Lumo logo when opened (at same position as collapsed toggle button) -->
          <div v-if="!sidebarCollapsed" class="sidebar-logo">
            <img src="/sidebar_lumo.svg" alt="Lumo" class="sidebar-logo-icon" />
          </div>

          <button
            class="sidebar-icon-btn"
            :class="{ active: activeSidebarTab === 'routing' }"
            @click.stop="handleIconClick('routing')"
            aria-label="Routing"
          >
            <img
              src="/routing_icon.svg"
              alt="Routing"
              class="sidebar-icon-img"
              aria-hidden="true"
            />
            <span class="sidebar-icon-tooltip">Routing</span>
          </button>
          <button
            class="sidebar-icon-btn"
            :class="{ active: activeSidebarTab === 'layers' }"
            @click.stop="handleIconClick('layers')"
            aria-label="Layers"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
            <span class="sidebar-icon-tooltip">Layers</span>
          </button>
          <button
            class="sidebar-icon-btn"
            :class="{ active: activeSidebarTab === 'route-history' }"
            @click.stop="handleIconClick('route-history')"
            aria-label="Route History"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            <span v-if="showHistoryIndicator" class="history-indicator"></span>
            <span class="sidebar-icon-tooltip">Route History</span>
          </button>
          <button
            class="sidebar-icon-btn sidebar-icon-btn--settings"
            :class="{ active: activeSidebarTab === 'settings' }"
            @click.stop="handleIconClick('settings')"
            aria-label="Settings"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path
                d="M11.52 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
              />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <span class="sidebar-icon-tooltip">Settings</span>
          </button>
        </div>

        <!-- Profile in icon bar when collapsed -->
        <div v-if="sidebarCollapsed" class="profile">
          <div class="info">
            <div class="name">John Doe</div>
            <div class="tier">Plus</div>
          </div>
        </div>
      </div>

      <!-- Divider line (only when expanded) -->
      <div v-if="!sidebarCollapsed" class="sidebar-divider"></div>

      <!-- Avatar positioned outside sidebar-main to avoid fade-in - always visible -->
      <div
        class="profile-avatar-fixed"
        :class="{ 'profile-avatar-fixed--collapsed': sidebarCollapsed }"
      >
        <div class="avatar">JD</div>
      </div>

      <!-- Main content area -->
      <div class="sidebar-main">
        <div class="sidebar-header">
          <div class="sidebar-header-content">
            <h2 class="nowrap">Lumo <span class="lumo-pro-thin">Pro</span></h2>
          </div>

          <!-- square collapse button (quadratic) - only when expanded -->
          <button
            v-if="!sidebarCollapsed"
            class="sidebar-toggle"
            :class="{ 'sidebar-toggle--will-close': !sidebarCollapsed }"
            @click="handleToggleSidebar"
            @mouseenter="handleSidebarToggleHover"
            @mouseleave="handleSidebarToggleLeave"
            :aria-expanded="!sidebarCollapsed"
            :aria-label="sidebarCollapsed ? 'Open sidebar' : 'Close sidebar'"
          >
            <img
              src="/sidebar.svg"
              alt="Toggle sidebar"
              class="sidebar-toggle-icon"
              aria-hidden="true"
            />
            <span class="sidebar-toggle-tooltip">
              {{ sidebarCollapsed ? "Open sidebar" : "Close sidebar" }}
            </span>
          </button>
        </div>

        <!-- Section Title Display -->
        <div v-if="!sidebarCollapsed" class="sidebar-section-title">
          <h3 class="sidebar-section-title-text">{{ sectionTitle }}</h3>
          <p class="sidebar-section-title-hint">{{ sectionHint }}</p>
        </div>

        <!-- Scrollable content area -->
        <div
          ref="scrollableRef"
          class="sidebar-scrollable"
          :class="{ 'sidebar-scrollable--scrolling': isScrolling }"
        >
          <!-- Routing section -->
          <div
            v-show="activeSidebarTab === 'routing'"
            class="group sidebar-content sidebar-routing"
          >
            <div class="section-content">
              <!-- Route planning -->
              <div class="route-planning-container">
                <div class="route-inputs-clean">
                  <!-- Input fields -->
                  <div class="route-inputs-wrapper">
                    <!-- Connector line spanning both groups -->
                    <div class="route-connector-line"></div>
                    <div class="route-input-group">
                      <!-- Left graphics -->
                      <div class="route-input-graphics">
                        <div class="route-icon route-icon--start">
                          <svg
                            width="10"
                            height="10"
                            viewBox="0 0 10 10"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <circle
                              cx="5"
                              cy="5"
                              r="4.5"
                              stroke="currentColor"
                              stroke-width="0.8"
                              fill="none"
                            />
                            <circle
                              cx="5"
                              cy="5"
                              r="2.5"
                              stroke="currentColor"
                              stroke-width="0.8"
                              fill="none"
                            />
                          </svg>
                        </div>
                      </div>
                      <div class="route-input-content">
                        <label
                          class="route-label-float"
                          :class="{ 'route-label-float--active': startHub }"
                          >From</label
                        >
                        <div class="route-select-wrapper">
                          <select
                            ref="startHubSelectRef"
                            v-model="startHub"
                            class="route-select"
                            @change="handleHubSelectChange($event, 'start')"
                            @blur="handleSelectBlur"
                          >
                            <option disabled value=""></option>
                            <option
                              v-for="h in displayedHubs"
                              :key="h.id"
                              :value="h.id"
                              :class="{
                                'option-show-more': h.id === 'show_more',
                              }"
                              :style="
                                h.id === 'show_more'
                                  ? 'font-weight: bold; font-style: italic;'
                                  : ''
                              "
                            >
                              {{ h.name }}
                            </option>
                          </select>
                          <button
                            v-if="startHub"
                            class="route-select-clear"
                            @click.stop="startHub = ''"
                            type="button"
                            aria-label="Clear selection"
                          >
                            <svg
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="2"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            >
                              <line x1="18" y1="6" x2="6" y2="18" />
                              <line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>

                    <div class="route-input-group">
                      <!-- Left graphics -->
                      <div class="route-input-graphics">
                        <div class="route-icon route-icon--end">
                          <svg
                            width="10"
                            height="10"
                            viewBox="0 0 10 10"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <circle
                              cx="5"
                              cy="5"
                              r="4.5"
                              stroke="currentColor"
                              stroke-width="0.8"
                              fill="none"
                            />
                            <circle
                              cx="5"
                              cy="5"
                              r="2.5"
                              stroke="currentColor"
                              stroke-width="0.8"
                              fill="none"
                            />
                          </svg>
                        </div>
                      </div>
                      <div class="route-input-content">
                        <label
                          class="route-label-float"
                          :class="{ 'route-label-float--active': endHub }"
                          >To</label
                        >
                        <div class="route-select-wrapper">
                          <select
                            ref="endHubSelectRef"
                            v-model="endHub"
                            class="route-select"
                            @change="handleHubSelectChange($event, 'end')"
                            @blur="handleSelectBlur"
                          >
                            <option disabled value=""></option>
                            <option
                              v-for="h in displayedHubs"
                              :key="h.id"
                              :value="h.id"
                              :class="{
                                'option-show-more': h.id === 'show_more',
                              }"
                              :style="
                                h.id === 'show_more'
                                  ? 'font-weight: bold; font-style: italic;'
                                  : ''
                              "
                            >
                              {{ h.name }}
                            </option>
                          </select>
                          <button
                            v-if="endHub"
                            class="route-select-clear"
                            @click.stop="endHub = ''"
                            type="button"
                            aria-label="Clear selection"
                          >
                            <svg
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="2"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            >
                              <line x1="18" y1="6" x2="6" y2="18" />
                              <line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Clear Route Button -->
              <div
                v-if="startHub || endHub || currentRouteStats"
                class="route-clear-section"
              >
                <button
                  class="route-clear-button"
                  @click="handleClearRoute"
                  type="button"
                  aria-label="Clear route"
                >
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path
                      d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                    />
                  </svg>
                </button>
              </div>

              <!-- Summary Display -->
            </div>
          </div>

          <!-- Layers -->
          <div
            v-show="activeSidebarTab === 'layers'"
            class="group sidebar-content"
          >
            <div class="section-content">
              <!-- Layer Types Category -->
              <div class="layers-category">
                <div
                  class="title-collapsible"
                  @click="layersCategoryExpanded = !layersCategoryExpanded"
                >
                  <span class="title">Layer Types</span>
                  <span
                    class="chevron chevron-category"
                    :class="{ 'chevron--expanded': layersCategoryExpanded }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{
                    'category-content--collapsed': !layersCategoryExpanded,
                  }"
                >
                  <button
                    :class="{ active: lightingVisible }"
                    @click="selectLayer('lighting')"
                  >
                    Lighting Intensity
                  </button>
                  <button
                    :class="{ active: vibrancyVisible }"
                    @click="selectLayer('vibrancy')"
                  >
                    Urban Vibrancy
                  </button>
                  <button
                    :class="{ active: combinedVisible }"
                    @click="selectLayer('combined')"
                  >
                    Combined Score
                  </button>
                </div>
              </div>

              <!-- Routing Hubs Category -->
              <div class="layers-category">
                <div
                  class="title-collapsible"
                  @click="
                    routingHubsCategoryExpanded = !routingHubsCategoryExpanded
                  "
                >
                  <span class="title">Routing</span>
                  <span
                    class="chevron chevron-category"
                    :class="{
                      'chevron--expanded': routingHubsCategoryExpanded,
                    }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{
                    'category-content--collapsed': !routingHubsCategoryExpanded,
                  }"
                >
                  <button
                    :class="{ active: routingHubsVisible }"
                    @click="toggleRoutingHubs"
                  >
                    Routing Hubs
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Route History -->
          <div
            v-show="activeSidebarTab === 'route-history'"
            class="group sidebar-content"
          >
            <div class="section-content">
              <div class="route-history-container">
                <div v-if="routeHistory.length > 0" class="route-history-title">
                  Today
                </div>
                <div class="route-history-list">
                  <div
                    v-if="routeHistory.length === 0"
                    class="route-history-empty"
                  >
                    No route history yet
                  </div>
                  <div
                    v-for="(entry, index) in routeHistory"
                    :key="index"
                    class="route-history-item"
                    @click="loadHistoryRoute(entry)"
                  >
                    <div class="route-history-route">
                      <span class="route-history-from">{{
                        entry.fromName
                      }}</span>
                      <svg
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        class="route-history-arrow"
                      >
                        <path d="M5 12h14M12 5l7 7-7 7" />
                      </svg>
                      <span class="route-history-to">{{ entry.toName }}</span>
                    </div>
                    <div class="route-history-date">
                      {{ entry.time || formatTimeOnly(entry.date) }}
                    </div>
                  </div>
                </div>
                <div class="route-history-clear-header">
                  <button
                    v-if="routeHistory.length > 0"
                    class="route-history-clear-btn"
                    @click.stop="clearHistory"
                    type="button"
                    title="Clear history"
                    aria-label="Clear history"
                  >
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <path
                        d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Settings -->
          <div
            v-show="activeSidebarTab === 'settings'"
            class="group sidebar-content"
          >
            <div class="section-content">
              <!-- Settings Navigation - Compact Category List -->
              <div class="settings-nav-compact">
                <div
                  v-for="category in settingsCategories"
                  :key="category.id"
                  class="settings-nav-item"
                  :class="{
                    'settings-nav-item--active': getCategoryExpanded(
                      category.id
                    ),
                  }"
                  @click="toggleAndScrollToCategory(category.id)"
                >
                  <span class="settings-nav-item-icon">
                    {{ getCategoryExpanded(category.id) ? "▼" : "▶" }}
                  </span>
                  <span class="settings-nav-item-label">{{
                    category.label
                  }}</span>
                </div>
              </div>

              <!-- Imprint Category -->
              <div
                id="settings-imprint"
                class="layers-category settings-category"
              >
                <div
                  class="title-collapsible"
                  @click="imprintExpanded = !imprintExpanded"
                >
                  <span class="title">Imprint</span>
                  <span
                    class="chevron chevron-category"
                    :class="{ 'chevron--expanded': imprintExpanded }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{ 'category-content--collapsed': !imprintExpanded }"
                >
                  <div class="settings-content">
                    <div class="settings-section">
                      <h4 class="settings-section-title">
                        Company Information
                      </h4>
                      <p class="settings-text">Your Company Name</p>
                      <p class="settings-text">Address Line 1</p>
                      <p class="settings-text">Address Line 2</p>
                      <p class="settings-text">City, Postal Code</p>
                      <p class="settings-text">Country</p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Contact</h4>
                      <p class="settings-text">Email: contact@example.com</p>
                      <p class="settings-text">Phone: +41 XX XXX XX XX</p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Legal Information</h4>
                      <p class="settings-text">VAT ID: XX-XXX-XXX</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Privacy Policy Category -->
              <div
                id="settings-privacy"
                class="layers-category settings-category"
              >
                <div
                  class="title-collapsible"
                  @click="privacyExpanded = !privacyExpanded"
                >
                  <span class="title">Privacy Policy</span>
                  <span
                    class="chevron chevron-category"
                    :class="{ 'chevron--expanded': privacyExpanded }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{ 'category-content--collapsed': !privacyExpanded }"
                >
                  <div class="settings-content">
                    <p class="settings-text settings-meta">
                      Last updated: [Date]
                    </p>
                    <div class="settings-section">
                      <p class="settings-text">
                        We respect your privacy and are committed to protecting
                        your personal data. This privacy policy explains how we
                        collect, use, and safeguard your information when you
                        use our application.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Data Collection</h4>
                      <p class="settings-text">
                        We collect information that you provide directly to us,
                        including route planning data and preferences.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Data Usage</h4>
                      <p class="settings-text">
                        Your data is used to provide and improve our services,
                        including route planning and map visualization features.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Data Protection</h4>
                      <p class="settings-text">
                        We implement appropriate technical and organizational
                        measures to protect your personal data.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Terms of Service Category -->
              <div
                id="settings-terms"
                class="layers-category settings-category"
              >
                <div
                  class="title-collapsible"
                  @click="termsExpanded = !termsExpanded"
                >
                  <span class="title">Terms of Service</span>
                  <span
                    class="chevron chevron-category"
                    :class="{ 'chevron--expanded': termsExpanded }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{ 'category-content--collapsed': !termsExpanded }"
                >
                  <div class="settings-content">
                    <p class="settings-text settings-meta">
                      Last updated: [Date]
                    </p>
                    <div class="settings-section">
                      <p class="settings-text">
                        By using this application, you agree to be bound by
                        these Terms of Service.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Use of Service</h4>
                      <p class="settings-text">
                        You may use this service for lawful purposes only. You
                        agree not to misuse the service or attempt to gain
                        unauthorized access.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">
                        Intellectual Property
                      </h4>
                      <p class="settings-text">
                        All content, features, and functionality of this
                        application are owned by us and are protected by
                        copyright and other intellectual property laws.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">
                        Limitation of Liability
                      </h4>
                      <p class="settings-text">
                        We are not liable for any indirect, incidental, or
                        consequential damages arising from your use of this
                        service.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- About Category -->
              <div
                id="settings-about"
                class="layers-category settings-category"
              >
                <div
                  class="title-collapsible"
                  @click="aboutExpanded = !aboutExpanded"
                >
                  <span class="title">About</span>
                  <span
                    class="chevron chevron-category"
                    :class="{ 'chevron--expanded': aboutExpanded }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{ 'category-content--collapsed': !aboutExpanded }"
                >
                  <div class="settings-content">
                    <div class="settings-section">
                      <h4 class="settings-section-title">About Lumo Pro</h4>
                      <p class="settings-text">
                        Lumo Pro is an advanced mapping and routing application
                        designed to help you explore and navigate urban
                        environments.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Features</h4>
                      <ul class="settings-list-items">
                        <li>Interactive map visualization</li>
                        <li>Route planning between hubs</li>
                        <li>
                          Multiple data layers (Lighting, Vibrancy, Combined)
                        </li>
                        <li>Real-time statistics and analytics</li>
                      </ul>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Version</h4>
                      <p class="settings-text">Version 1.0.0</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Contact Category -->
              <div
                id="settings-contact"
                class="layers-category settings-category"
              >
                <div
                  class="title-collapsible"
                  @click="contactExpanded = !contactExpanded"
                >
                  <span class="title">Contact</span>
                  <span
                    class="chevron chevron-category"
                    :class="{ 'chevron--expanded': contactExpanded }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{ 'category-content--collapsed': !contactExpanded }"
                >
                  <div class="settings-content">
                    <div class="settings-section">
                      <p class="settings-text">
                        We'd love to hear from you! Get in touch with us through
                        any of the following channels:
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Email</h4>
                      <p class="settings-text">contact@example.com</p>
                      <p class="settings-text">support@example.com</p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Phone</h4>
                      <p class="settings-text">+41 XX XXX XX XX</p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Address</h4>
                      <p class="settings-text">Your Company Name</p>
                      <p class="settings-text">Address Line 1</p>
                      <p class="settings-text">City, Postal Code</p>
                      <p class="settings-text">Country</p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Business Hours</h4>
                      <p class="settings-text">
                        Monday - Friday: 9:00 AM - 6:00 PM
                      </p>
                      <p class="settings-text">Saturday - Sunday: Closed</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Help / FAQ Category -->
              <div id="settings-help" class="layers-category settings-category">
                <div
                  class="title-collapsible"
                  @click="helpExpanded = !helpExpanded"
                >
                  <span class="title">Help / FAQ</span>
                  <span
                    class="chevron chevron-category"
                    :class="{ 'chevron--expanded': helpExpanded }"
                    >›</span
                  >
                </div>
                <div
                  class="category-content"
                  :class="{ 'category-content--collapsed': !helpExpanded }"
                >
                  <div class="settings-content">
                    <div class="settings-section">
                      <h4 class="settings-section-title">
                        How do I plan a route?
                      </h4>
                      <p class="settings-text">
                        Select a starting hub and destination hub from the
                        Routing section, then click "Plan Route".
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">
                        How do I change map layers?
                      </h4>
                      <p class="settings-text">
                        Go to the Layers section and select from Lighting,
                        Vibrancy, or Combined layers.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">
                        How do I view statistics?
                      </h4>
                      <p class="settings-text">
                        Click on the Statistics icon in the sidebar to view
                        detailed statistics and legend information.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">
                        Can I customize the map view?
                      </h4>
                      <p class="settings-text">
                        Yes! Use the map controls to zoom, rotate, and tilt the
                        map view.
                      </p>
                    </div>
                    <div class="settings-section">
                      <h4 class="settings-section-title">Need more help?</h4>
                      <p class="settings-text">
                        Contact us through the Contact section for additional
                        support.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile section (stays visible, text hides when collapsed) -->
        <div class="profile">
          <div class="info">
            <div class="name">John Doe</div>
            <div class="tier">Plus</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Hover popup -->
    <div
      v-if="popup.show"
      class="popup"
      :style="{ left: popup.x + 'px', top: popup.y + 'px' }"
    >
      <div class="row">
        <span>Lights</span><b>{{ popup.lights }}</b>
      </div>
      <div class="row">
        <span>POIs</span><b>{{ popup.pois }}</b>
      </div>
      <div class="row">
        <span>Nearest hub</span><b>{{ popup.hub }}</b>
      </div>
    </div>

    <!-- Walkthrough overlay shown on initial load -->
    <Walkthrough
      v-if="showWalkthrough"
      @close="showWalkthrough = false"
      @takeTour="startTour"
      @enterMap="focusZurich"
      :mapReady="mapReady"
    />
    <GuidedTour v-if="showGuidedTour" @close="finishTour" />

    <!-- Map Controls (Zoom and North) -->
    <div
      class="map-controls-over-scale"
      :class="{
        'map-controls-over-scale--basket-expanded': isBasketExpanded,
      }"
    >
      <button
        class="map-control-btn-over-scale"
        @click.stop="handleToggleFullscreen"
        aria-label="Toggle fullscreen"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"
          />
        </svg>
      </button>
      <button
        class="map-control-btn-over-scale"
        @click.stop="handleZoomIn"
        aria-label="Zoom in"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 5V19M5 12H19" />
        </svg>
      </button>
      <button
        class="map-control-btn-over-scale"
        @click.stop="handleZoomOut"
        aria-label="Zoom out"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M5 12H19" />
        </svg>
      </button>
      <button
        class="map-control-btn-over-scale"
        @click.stop="handleResetNorth"
        aria-label="Reset to north"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <polygon points="12 6 16 14 12 11 8 14 12 6" />
        </svg>
      </button>
    </div>

    <!-- Scale indicator -->
    <div
      class="map-scale"
      :class="{
        'map-scale--visible': mapZoom >= 12.5,
        'map-scale--sidebar-collapsed': sidebarCollapsed,
      }"
    >
      <div class="scale-line"></div>
      <div class="scale-label">{{ scaleText }}</div>
    </div>

    <!-- Click outside to close map controls -->
    <div
      v-if="mapControlsExpanded"
      class="map-controls-overlay"
      @click="mapControlsExpanded = false"
    ></div>

    <!-- Zurich App Button (top right corner) -->
    <!-- App Basket Container (Glassmorphic) -->
    <div
      class="app-basket"
      :class="{ 'app-basket--expanded': isBasketExpanded }"
    >
      <!-- Apps Container -->
      <div class="app-basket-apps-container">
        <!-- Animation App Button -->
        <div class="animation-app-container">
          <button
            class="animation-app-button"
            :class="{
              'animation-app-button--expanded': activeBasketApp === 'animation',
            }"
            @click.stop="toggleAnimation"
            aria-label="Animation"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
          </button>
        </div>

        <!-- Chat App Button -->
        <button
          class="chat-app-button"
          :class="{ 'chat-app-button--active': activeBasketApp === 'chat' }"
          @click.stop="toggleChat"
          aria-label="Open chat"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
            ></path>
            <line x1="9" y1="10" x2="15" y2="10"></line>
          </svg>
        </button>

        <!-- Legend App Button -->
        <button
          class="legend-app-button"
          :class="{ 'legend-app-button--active': activeBasketApp === 'legend' }"
          @click.stop="toggleLegend"
          aria-label="Open legend"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
        </button>

        <!-- Security App Button -->
        <button
          class="security-app-button"
          :class="{
            'security-app-button--active': activeBasketApp === 'security',
          }"
          @click.stop="toggleSecurity"
          aria-label="Open security"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
        </button>

        <!-- Zurich App Button (on the right) -->
        <div class="zurich-app-button" @click.stop="closeBasket">
          <!-- Zoom to Zurich Button (shown when zoomed out) -->
          <button
            v-if="mapZoom < 11.5"
            class="zurich-app-button-inner"
            @click="focusZurich(true)"
            aria-label="Zoom to Zurich"
          >
            <svg
              class="zurich-app-icon"
              width="24"
              height="24"
              viewBox="0 0 32.42 39.57"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M16.21,0C7.27,0,0,7.27,0,16.21c0,2.57.59,5.04,1.73,7.29,3.17,7.01,9.89,13.08,12.62,15.35.39.35,1.09.72,1.89.72.65,0,1.26-.24,1.79-.7,2.75-2.28,9.48-8.35,12.63-15.33,1.16-2.29,1.75-4.76,1.75-7.33C32.42,7.27,25.15,0,16.21,0ZM30.66,16.21c0,2.29-.53,4.5-1.57,6.55v.02c-3.02,6.68-9.53,12.53-12.19,14.75-.64.56-1.23.14-1.4-.01-2.65-2.2-9.15-8.06-12.18-14.77-1.04-2.04-1.56-4.24-1.56-6.53C1.76,8.24,8.24,1.76,16.21,1.76s14.45,6.48,14.45,14.45Z"
                fill="#ffffff"
              />
            </svg>
          </button>

          <!-- Location & Time Display (shown when zoomed in) -->
          <div
            v-else-if="mapZoom >= 11.5 && locationText"
            class="zurich-app-location"
          >
            <div class="zurich-app-location-name">{{ locationText }}</div>
            <div class="zurich-app-location-time">
              <span class="zurich-app-time-text" v-if="zurichTime">
                {{ zurichTime }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Expanded App Content -->
      <transition name="basket-expand">
        <div v-if="isBasketExpanded" class="app-basket-content">
          <!-- App label -->
          <transition name="label-fade" mode="out-in">
            <div :key="activeBasketApp" class="app-basket-content-label">
              <span v-if="activeBasketApp === 'chat'">Route Companion</span>
              <span v-else-if="activeBasketApp === 'legend'">Legend</span>
              <span v-else-if="activeBasketApp === 'security'">Security</span>
              <span v-else-if="activeBasketApp === 'animation'">Animation</span>
            </div>
          </transition>

          <!-- Close button (chevron up) -->
          <button
            class="app-basket-content-close"
            @click="closeBasket"
            aria-label="Close app"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M18 15l-6-6-6 6" />
            </svg>
          </button>

          <!-- App content (scrollable) with reload animation -->
          <transition name="basket-reload" mode="out-in">
            <div
              :key="
                activeBasketApp === 'legend'
                  ? `legend-${mode}`
                  : activeBasketApp
              "
              class="app-basket-content-scrollable-wrapper"
              :class="{
                'route-already-shown':
                  activeBasketApp === 'chat' && isCurrentRouteAlreadyShown,
              }"
            >
              <div
                class="app-basket-content-scrollable"
                ref="chatScrollableRef"
              >
                <!-- Chat App Content -->
                <div
                  v-if="activeBasketApp === 'chat'"
                  class="app-basket-app-section"
                  :class="{ 'route-already-shown': isCurrentRouteAlreadyShown }"
                >
                  <!-- Route info section -->
                  <div
                    v-if="currentRouteStats"
                    class="route-details-popup-info"
                  >
                    <div class="route-details-intro">
                      <div class="route-details-intro-greeting">
                        <span class="route-details-greeting-bold">{{
                          currentGreeting
                        }}</span>
                      </div>
                      <div class="route-details-intro-text">
                        Here are some insights about your route:
                      </div>
                    </div>
                  </div>

                  <!-- Empty state when no route is selected -->
                  <div v-else class="route-details-popup-info"></div>

                  <!-- Combined POI Statistics for Both Routes -->
                  <div
                    v-if="mergedRouteHighlights.length > 0"
                    class="route-details-document"
                  >
                    <div class="route-details-document-header">
                      <svg
                        class="route-details-document-icon"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path
                          d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                        ></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                      </svg>
                      <span class="route-details-document-title"
                        >Route highlights</span
                      >
                    </div>
                    <div class="route-details-document-content">
                      <div
                        v-for="highlight in mergedRouteHighlights"
                        :key="highlight.poiType"
                        class="route-details-document-item"
                      >
                        <div class="route-details-document-item-icon">
                          <div
                            class="route-details-poi-icon"
                            v-html="getPoiIcon(highlight.poiType)"
                          ></div>
                        </div>
                        <div class="route-details-document-item-info">
                          <div
                            v-if="
                              highlight.fastFreq || highlight.brightFreq
                            "
                            class="route-details-poi-frequency"
                          >
                            <template v-if="highlight.fastFreq && highlight.brightFreq">
                              {{ formatPoiFrequency(highlight.poiType, highlight.fastFreq) }}
                              <span class="route-details-poi-frequency-bright">
                                ({{ extractTimeFromFrequency(highlight.brightFreq) }})
                              </span>
                            </template>
                            <template v-else-if="highlight.fastFreq">
                              {{ formatPoiFrequency(highlight.poiType, highlight.fastFreq) }}
                            </template>
                            <template v-else-if="highlight.brightFreq">
                              <span class="route-details-poi-frequency-bright">
                                {{ formatPoiFrequency(highlight.poiType, highlight.brightFreq) }}
                              </span>
                            </template>
                          </div>
                          <div class="route-details-poi-mantra">
                            {{ getPoiMantra(highlight.poiType) }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Empty state when no route highlights available -->
                  <div
                    v-else-if="
                      currentRouteStats &&
                      mergedRouteHighlights.length === 0
                    "
                    class="route-details-empty"
                  >
                    <p class="route-details-empty-text">
                      Clear route, peaceful walk
                    </p>
                  </div>

                  <div v-if="currentRouteStats" class="route-details-footer">
                    <div class="route-details-footer-bubble">
                      You're all set! Enjoy your walk through the city.
                    </div>

                    <!-- User message bubble (shown after user sends) -->
                    <div
                      v-if="
                        userMessageSent &&
                        sentUserMessage &&
                        isCurrentRouteMessages
                      "
                      class="route-details-user-message"
                    >
                      {{ sentUserMessage }}
                    </div>

                    <!-- Response bubbles (shown after user sends message) -->
                    <div
                      v-if="userMessageSent && isCurrentRouteMessages"
                      class="route-details-response-section"
                      :class="{
                        'response-already-shown': shouldSkipResponseAnimations,
                      }"
                    >
                      <div class="route-details-response-bubble">
                        No worries!
                      </div>
                      <div class="route-details-safety-bubble">
                        If you don't feel safe, head to the nearest café or
                        restaurant where people are around.
                      </div>
                    </div>
                  </div>

                  <!-- Empty state footer message -->
                  <div v-else class="route-details-footer">
                    <div
                      class="route-details-footer-bubble route-details-footer-bubble--greeting route-details-footer-bubble--welcome"
                    >
                      Hey there!
                    </div>
                    <div
                      class="route-details-footer-bubble route-details-footer-bubble--welcome"
                      style="margin-top: 8px"
                    >
                      I find the best routes through Zurich with data on
                      lighting, vibrancy, and safety.
                    </div>
                    <div
                      class="route-details-footer-bubble route-details-footer-bubble--welcome"
                      style="margin-top: 8px"
                    >
                      Click the colored dots on the map, or use the routing tool
                      in the sidebar
                      <button
                        class="route-details-footer-button"
                        @click.stop="handleOpenRoutingTool"
                      >
                        here
                      </button>
                      .
                    </div>
                    <!-- Learn More Document Attachment -->
                    <div
                      class="route-details-document route-details-footer-bubble--welcome"
                      style="margin-top: 12px"
                    >
                      <div
                        class="route-details-document-header"
                        @click.stop="isAboutLumoExpanded = !isAboutLumoExpanded"
                        style="cursor: pointer"
                      >
                        <svg
                          class="route-details-document-icon"
                          width="16"
                          height="16"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        >
                          <circle cx="12" cy="12" r="10"></circle>
                          <line x1="12" y1="16" x2="12" y2="12"></line>
                          <line x1="12" y1="8" x2="12.01" y2="8"></line>
                        </svg>
                        <span class="route-details-document-title"
                          >Find out more about me</span
                        >
                        <svg
                          class="route-details-document-chevron"
                          :class="{
                            'route-details-document-chevron--expanded':
                              isAboutLumoExpanded,
                          }"
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        >
                          <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                      </div>
                      <transition name="document-expand">
                        <div
                          v-if="isAboutLumoExpanded"
                          class="route-details-document-content"
                        >
                          <div class="route-details-document-text">
                            I analyze routes using real data on lighting,
                            vibrancy, and safety. Every route shows these
                            insights so you can choose what fits you.
                          </div>
                        </div>
                      </transition>
                    </div>
                  </div>
                </div>

                <!-- Legend App Content -->
                <div
                  v-else-if="activeBasketApp === 'legend'"
                  class="app-basket-app-section"
                >
                  <Legend
                    :mode="mode"
                    :in-box="true"
                    :dragged-out="false"
                    :hubs="hubs"
                    :mapZoom="mapZoom"
                    @openLayersSection="handleOpenLayersSection"
                    @hotspotClicked="handleHotspotClick"
                  />
                </div>

                <!-- Security App Content -->
                <div
                  v-else-if="activeBasketApp === 'security'"
                  class="app-basket-app-section"
                >
                  <div class="app-basket-security-content">
                    <h3 class="security-content-title">Security & Safety</h3>
                    <p class="security-introduction">
                      Your safety is our priority. Access emergency contacts and
                      route safety information to help you navigate Zurich with
                      confidence.
                    </p>

                    <!-- Route Security Alerts -->
                    <div class="security-category" style="margin-top: 32px">
                      <h4 class="security-category-title">Route Safety</h4>
                      <button
                        class="security-alert-button"
                        :class="{ active: routeSecurityAlertsActive }"
                        @click="toggleRouteSecurityAlerts"
                        :disabled="!currentRouteStats"
                      >
                        <svg
                          width="16"
                          height="16"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        >
                          <path
                            d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
                          ></path>
                          <path d="M12 8v4"></path>
                          <path d="M12 16h.01"></path>
                        </svg>
                        <span
                          >{{
                            routeSecurityAlertsActive ? "Hide" : "Show"
                          }}
                          Security Alerts</span
                        >
                      </button>
                      <p
                        class="security-alert-description"
                        v-if="!currentRouteStats"
                      >
                        Select a route to view security alerts
                      </p>
                      <p
                        class="security-alert-description"
                        v-else-if="routeSecurityAlertsActive"
                      >
                        Route segments passing through unsafe areas are
                        highlighted in red
                      </p>
                      <div
                        v-if="currentRouteStats && routeLumoScores"
                        class="lumo-score-display"
                        style="margin-top: 16px"
                      >
                        <div class="lumo-score-label">Lumo Score</div>
                        <div class="lumo-score-values">
                          <div
                            v-if="routeLumoScores.fast"
                            class="lumo-score-item"
                          >
                            <span class="lumo-score-route-type">Fast:</span>
                            <span class="lumo-score-number">{{
                              formatLumoScore(routeLumoScores.fast.lumo_score)
                            }}</span>
                          </div>
                          <div
                            v-if="routeLumoScores.bright"
                            class="lumo-score-item"
                          >
                            <span class="lumo-score-route-type">Bright:</span>
                            <span class="lumo-score-number">{{
                              formatLumoScore(routeLumoScores.bright.lumo_score)
                            }}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Link Route to Uber -->
                    <div class="security-category" style="margin-top: 32px">
                      <h4 class="security-category-title">
                        Link Route to Uber
                      </h4>
                      <div class="uber-link-section">
                        <div class="uber-icon-container">
                          <img
                            class="uber-icon"
                            :src="`${BASE}assets/uber.jpg`"
                            alt="Uber"
                          />
                        </div>
                        <p class="uber-description">
                          Transfer your route details directly to the Uber app
                          for convenient ride booking. Your selected route will
                          be imported with start and destination points ready
                          for booking.
                        </p>
                        <button
                          class="uber-import-button"
                          :disabled="!currentRouteStats"
                          @click="handleUberImport"
                        >
                          <svg
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          >
                            <path
                              d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"
                            ></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                          </svg>
                          <span>Import Route Details into Uber</span>
                        </button>
                      </div>
                    </div>

                    <!-- Emergency Numbers -->
                    <div class="security-category" style="margin-top: 32px">
                      <h4 class="security-category-title">Emergency Numbers</h4>
                      <div class="security-contacts-table">
                        <div class="security-contacts-header">
                          <div class="security-contact-facility">Service</div>
                          <div class="security-contact-number">
                            Phone Number
                          </div>
                        </div>
                        <div class="security-contact-row">
                          <div class="security-contact-facility">
                            General Emergency
                          </div>
                          <div class="security-contact-number">
                            <a href="tel:112" class="security-contact-link"
                              >112</a
                            >
                          </div>
                        </div>
                        <div class="security-contact-row">
                          <div class="security-contact-facility">Police</div>
                          <div class="security-contact-number">
                            <a href="tel:117" class="security-contact-link"
                              >117</a
                            >
                          </div>
                        </div>
                        <div class="security-contact-row">
                          <div class="security-contact-facility">
                            Fire Department
                          </div>
                          <div class="security-contact-number">
                            <a href="tel:118" class="security-contact-link"
                              >118</a
                            >
                          </div>
                        </div>
                        <div class="security-contact-row">
                          <div class="security-contact-facility">
                            Medical Emergency
                          </div>
                          <div class="security-contact-number">
                            <a href="tel:144" class="security-contact-link"
                              >144</a
                            >
                          </div>
                        </div>
                        <div class="security-contact-row">
                          <div class="security-contact-facility">
                            Poison Control
                          </div>
                          <div class="security-contact-number">
                            <a href="tel:145" class="security-contact-link"
                              >145</a
                            >
                          </div>
                        </div>
                        <div class="security-contact-row">
                          <div class="security-contact-facility">
                            Roadside Assistance
                          </div>
                          <div class="security-contact-number">
                            <a href="tel:140" class="security-contact-link"
                              >140</a
                            >
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Animation App Content -->
                <div
                  v-else-if="activeBasketApp === 'animation'"
                  class="app-basket-app-section"
                >
                  <div class="app-basket-animation-content">
                    <div class="animation-content">
                      <p class="animation-description">
                        Animate the display of hexagons that intersect with the
                        current routes.
                      </p>

                      <!-- Coloring Mode Selector -->
                      <div class="animation-coloring-mode">
                        <label class="animation-coloring-label"
                          >Display Style</label
                        >
                        <div class="animation-coloring-options">
                          <button
                            class="animation-coloring-button"
                            :class="{
                              active: animationColoringMode === 'route',
                            }"
                            @click="animationColoringMode = 'route'"
                            :disabled="!routeAnimationActive"
                          >
                            <span>Route Style</span>
                            <span class="animation-coloring-hint"
                              >Blue and grey colors</span
                            >
                          </button>
                          <button
                            class="animation-coloring-button"
                            :class="{
                              active: animationColoringMode === 'median',
                            }"
                            @click="animationColoringMode = 'median'"
                            :disabled="!routeAnimationActive"
                          >
                            <span>Safety Comparison</span>
                            <span class="animation-coloring-hint"
                              >Green (safer) / Red (less safe)</span
                            >
                          </button>
                        </div>
                      </div>

                      <button
                        class="animation-button"
                        @click="handleAnimateRoutes"
                        :disabled="!currentRouteStats || isAnimating"
                      >
                        <svg
                          v-if="!isAnimating"
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        >
                          <polygon points="5 3 19 12 5 21 5 3"></polygon>
                        </svg>
                        <svg
                          v-else
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        >
                          <rect x="6" y="4" width="4" height="16"></rect>
                          <rect x="14" y="4" width="4" height="16"></rect>
                        </svg>
                        <span>{{
                          isAnimating ? "Animating..." : "Animate Routes"
                        }}</span>
                      </button>
                      <button
                        v-if="isAnimating || routeAnimationActive"
                        class="animation-reset-button"
                        @click="handleResetAnimation"
                      >
                        <svg
                          width="16"
                          height="16"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        >
                          <polyline points="23 4 23 10 17 10"></polyline>
                          <polyline points="1 20 1 14 7 14"></polyline>
                          <path
                            d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"
                          ></path>
                        </svg>
                        <span>Reset</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>

          <!-- Floating input button/box (only for chat) -->
          <div
            v-if="activeBasketApp === 'chat'"
            class="route-details-input-container"
          >
            <input
              v-if="showInput"
              v-model="userMessage"
              @keyup.enter="handleSendMessage"
              @blur="showInput = false"
              type="text"
              placeholder="Type a message..."
              class="route-details-input"
              ref="inputRef"
            />
            <button
              v-else
              @click="openInput"
              class="route-details-input-button"
              aria-label="Type a message"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                ></path>
                <line x1="9" y1="10" x2="15" y2="10"></line>
              </svg>
            </button>
          </div>
        </div>
      </transition>
    </div>

    <!-- Legend Popup -->
    <transition name="route-details-slide">
      <div
        v-if="legendPopupVisible"
        class="route-details-popup-overlay"
        @click="legendPopupVisible = false"
      >
        <div class="route-details-popup legend-popup" @click.stop>
          <!-- Legend label -->
          <div class="route-details-popup-label">Legend</div>

          <!-- Close button -->
          <button
            class="route-details-popup-close"
            @click="legendPopupVisible = false"
            aria-label="Close legend"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>

          <!-- Legend content -->
          <div class="route-details-popup-content">
            <div class="legend-popup-content">
              <Legend
                :mode="mode"
                :in-box="true"
                :dragged-out="false"
                :mapZoom="mapZoom"
                @hotspotClicked="handleHotspotClick"
              />
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
  nextTick,
  watch,
} from "vue";
import MapboxViewer from "./components/MapboxViewer.vue";
import Legend from "./components/Legend.vue";
import Walkthrough from "./components/Walkthrough.vue";
import GuidedTour from "./components/GuidedTour.vue";

// UI state
const heightScale = ref(1.5);
// Layer visibility states - only one can be active at a time
const lightingVisible = ref(false);
const vibrancyVisible = ref(false);
const combinedVisible = ref(false);

// Function to select/deselect a layer (only one can be active at a time)
function selectLayer(layerName) {
  // Check if the clicked layer is already active
  const isCurrentlyActive =
    (layerName === "lighting" && lightingVisible.value) ||
    (layerName === "vibrancy" && vibrancyVisible.value) ||
    (layerName === "combined" && combinedVisible.value);

  if (isCurrentlyActive) {
    // If already active, deselect it
    lightingVisible.value = false;
    vibrancyVisible.value = false;
    combinedVisible.value = false;
  } else {
    // Otherwise, select this layer and deselect others
    lightingVisible.value = layerName === "lighting";
    vibrancyVisible.value = layerName === "vibrancy";
    combinedVisible.value = layerName === "combined";
  }
}

// Computed mode for Legend component
const mode = computed(() => {
  if (combinedVisible.value) return "combined";
  if (vibrancyVisible.value) return "vibrancy";
  if (lightingVisible.value) return "lighting";
  return null; // No layer selected
});

// Computed property for active layer display name
const activeLayerName = computed(() => {
  if (combinedVisible.value) return "Combined Score";
  if (vibrancyVisible.value) return "Urban Vibrancy";
  if (lightingVisible.value) return "Lighting Intensity";
  return null;
});

// Function to clear the active layer
function clearActiveLayer() {
  lightingVisible.value = false;
  vibrancyVisible.value = false;
  combinedVisible.value = false;
}
const startHub = ref("");
const endHub = ref("");
const hubs = ref([]);
const showAllHubs = ref(false); // Track if "show more" is clicked
const startHubSelectRef = ref(null);
const endHubSelectRef = ref(null);
const routeHistory = ref([]);

// Computed property for limited hub list (4 hubs + "show more" option)
const displayedHubs = computed(() => {
  if (showAllHubs.value) {
    // When "show more" is clicked, show all hubs (without "Show more" option)
    return hubs.value;
  }

  // Collapsed state: Always return first 4 hubs + selected hubs (if not in first 4) + "Show more"
  const firstFour = hubs.value.slice(0, 4);
  const selectedHubIds = [startHub.value, endHub.value].filter(Boolean);
  const selectedHubs = selectedHubIds
    .map((id) => hubs.value.find((h) => h.id === id))
    .filter((h) => h && !firstFour.find((f) => f.id === h.id)); // Only include if not already in first 4

  // Combine first 4, selected hubs (if any), and "Show more" with arrow
  return [
    ...firstFour,
    ...selectedHubs,
    { id: "show_more", name: "Show more →" },
  ];
});
const currentRouteStats = ref(null);
const fastRouteStats = ref(null);
const brightRouteStats = ref(null);
const isLoadingFromHistory = ref(false); // Flag to prevent adding history routes to history
const isHandlingHubClicks = ref(false); // Flag to prevent watcher from triggering when handling hub clicks
const routeDetailsPopupVisible = ref(false);
// Track which routes have been shown in the chat app before
const routesShownInChat = ref([]);
// Track which routes have shown response bubbles (to skip animations on subsequent messages)
const routesWithResponseShown = ref([]);
// Track if About Lumo document is expanded
const isAboutLumoExpanded = ref(false);
// Track timeout for marking route as shown (to allow animations to complete)
let markRouteShownTimeout = null;
const legendPopupVisible = ref(false);
const phonePopupVisible = ref(false);
const userMessage = ref("");
const sentUserMessage = ref("");
const userMessageSent = ref(false);
const showInput = ref(false);
// Track which route the current messages belong to
const messagesRouteKey = ref(null);
const mapControlsExpanded = ref(false);
const displayedHotspotName = ref(null);
let hotspotNameTimeout = null;

// Track which app is currently active in the basket
const activeBasketApp = ref(null); // 'chat', 'legend', 'security', 'animation', or null
// Store previous app state to restore when zooming back in
const previousBasketApp = ref(null);

// Computed to check if basket should be expanded
const isBasketExpanded = computed(() => {
  return activeBasketApp.value !== null;
});

// Computed to check if current route has been shown in chat before
const isCurrentRouteAlreadyShown = computed(() => {
  if (activeBasketApp.value !== "chat") return false;
  if (!currentRouteStats.value || !startHub.value || !endHub.value)
    return false;
  const routeKey = `${startHub.value}-${endHub.value}`;
  return routesShownInChat.value.includes(routeKey);
});

// Computed to merge POI types from both routes for comparison
const mergedRouteHighlights = computed(() => {
  const merged = [];
  const allPoiTypes = new Set();
  
  // Collect all POI types from both routes
  if (fastRouteStats.value?.poiCounts) {
    Object.keys(fastRouteStats.value.poiCounts).forEach(type => allPoiTypes.add(type));
  }
  if (brightRouteStats.value?.poiCounts) {
    Object.keys(brightRouteStats.value.poiCounts).forEach(type => allPoiTypes.add(type));
  }
  
  // Create merged entries for each POI type
  allPoiTypes.forEach(poiType => {
    const fastFreq = fastRouteStats.value?.poiFrequencies?.[poiType];
    const brightFreq = brightRouteStats.value?.poiFrequencies?.[poiType];
    const fastCount = fastRouteStats.value?.poiCounts?.[poiType] || 0;
    const brightCount = brightRouteStats.value?.poiCounts?.[poiType] || 0;
    
    // Only include if at least one route has this POI type
    if (fastCount > 0 || brightCount > 0) {
      merged.push({
        poiType,
        fastFreq,
        brightFreq,
        fastCount,
        brightCount,
      });
    }
  });
  
  return merged;
});

// Computed to check if current messages belong to the current route
const isCurrentRouteMessages = computed(() => {
  if (!startHub.value || !endHub.value) return false;
  const currentRouteKey = `${startHub.value}-${endHub.value}`;
  return messagesRouteKey.value === currentRouteKey;
});

// Computed to check if response bubbles should skip animations (already shown for this route)
const shouldSkipResponseAnimations = computed(() => {
  if (!startHub.value || !endHub.value) return false;
  const currentRouteKey = `${startHub.value}-${endHub.value}`;
  return routesWithResponseShown.value.includes(currentRouteKey);
});

// Helper function to close basket (clears previous state to prevent auto-reopen)
function closeBasket() {
  activeBasketApp.value = null;
  previousBasketApp.value = null;
}

// Animation state
const isAnimating = ref(false);
const routeAnimationActive = ref(false);
const animationColoringMode = ref("route"); // "route" or "median"

// Route security alerts state
const routeSecurityAlertsActive = ref(false);
const routeLumoScores = ref(null);

// Handler functions for app buttons that clear previous state on manual interaction
function toggleAnimation() {
  previousBasketApp.value = null; // Clear previous state on manual interaction
  activeBasketApp.value =
    activeBasketApp.value === "animation" ? null : "animation";
}

// Handle route animation
async function handleAnimateRoutes() {
  if (!currentRouteStats.value || !startHub.value || !endHub.value) {
    console.warn("No route available for animation");
    return;
  }

  const routeApi = api || mapboxViewerRef.value;
  if (!routeApi || !routeApi.animateRouteHexagons) {
    console.warn("Animation function not available");
    return;
  }

  isAnimating.value = true;
  routeAnimationActive.value = true;

  try {
    const routeId1 = Math.min(parseInt(startHub.value), parseInt(endHub.value));
    const routeId2 = Math.max(parseInt(startHub.value), parseInt(endHub.value));

    await routeApi.animateRouteHexagons(
      routeId1,
      routeId2,
      animationColoringMode.value
    );
  } catch (error) {
    console.error("Error animating routes:", error);
  } finally {
    isAnimating.value = false;
  }
}

// Reset animation
function handleResetAnimation() {
  const routeApi = api || mapboxViewerRef.value;
  if (routeApi && routeApi.resetRouteAnimation) {
    routeApi.resetRouteAnimation();
  }
  routeAnimationActive.value = false;
  isAnimating.value = false;
}

// Watch for route changes and clear security alerts
watch([startHub, endHub], () => {
  if (routeSecurityAlertsActive.value) {
    routeSecurityAlertsActive.value = false;
  }
  // Load lumo scores when route changes
  loadRouteLumoScores();
});

// Load lumo scores for the current route
async function loadRouteLumoScores() {
  if (!startHub.value || !endHub.value) {
    routeLumoScores.value = null;
    return;
  }

  try {
    const routeId1 = Math.min(parseInt(startHub.value), parseInt(endHub.value));
    const routeId2 = Math.max(parseInt(startHub.value), parseInt(endHub.value));
    const routeName = `${routeId1}_${routeId2}`;

    const BASE = import.meta.env.BASE_URL || "/";
    const url =
      `${BASE}data/route_lumo_scores/${routeName}.json?v=${Date.now()}`.replace(
        /\/{2,}/g,
        "/"
      );

    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      routeLumoScores.value = data;
    } else {
      routeLumoScores.value = null;
    }
  } catch (error) {
    console.error("Failed to load lumo scores:", error);
    routeLumoScores.value = null;
  }
}

// Format lumo score for display
// lumo_score is the fraction of unsafe hexagons (0-1)
// We convert to 0-10 scale where 10.0 is perfect (no red hexagons), 0.0 is worst (all red)
// Formula: display_score = 10.0 * (1 - lumo_score)
function formatLumoScore(lumoScore) {
  if (lumoScore === null || lumoScore === undefined) return "N/A";

  // Convert from fraction of unsafe hexagons to 0-10 scale
  // 0 unsafe = 10.0 (perfect), 1 unsafe = 0.0 (worst)
  const displayScore = 10.0 * (1 - lumoScore);
  return displayScore.toFixed(1);
}

// Watch for coloring mode changes and update animation if active
watch(animationColoringMode, (newMode, oldMode) => {
  console.log(`Coloring mode changed from ${oldMode} to ${newMode}`);
  console.log("routeAnimationActive:", routeAnimationActive.value);
  console.log("currentRouteStats:", !!currentRouteStats.value);
  console.log("startHub:", startHub.value);
  console.log("endHub:", endHub.value);

  if (
    routeAnimationActive.value &&
    currentRouteStats.value &&
    startHub.value &&
    endHub.value
  ) {
    const routeApi = api || mapboxViewerRef.value;
    console.log("Route API available:", !!routeApi);
    console.log(
      "updateAnimationColoring available:",
      !!(routeApi && routeApi.updateAnimationColoring)
    );

    if (routeApi) {
      const routeId1 = Math.min(
        parseInt(startHub.value),
        parseInt(endHub.value)
      );
      const routeId2 = Math.max(
        parseInt(startHub.value),
        parseInt(endHub.value)
      );
      console.log(
        `Regenerating animation with route ${routeId1}_${routeId2}, mode: ${newMode}`
      );
      // Re-animate with new coloring mode to instantly regenerate
      if (routeApi.animateRouteHexagons) {
        routeApi.animateRouteHexagons(routeId1, routeId2, newMode);
      } else {
        console.warn("animateRouteHexagons not available");
      }
    } else {
      console.warn("Route API not available");
    }
  } else {
    console.warn("Cannot update coloring: conditions not met");
  }
});

function toggleChat() {
  previousBasketApp.value = null; // Clear previous state on manual interaction
  activeBasketApp.value = activeBasketApp.value === "chat" ? null : "chat";
}

function toggleLegend() {
  previousBasketApp.value = null; // Clear previous state on manual interaction
  activeBasketApp.value = activeBasketApp.value === "legend" ? null : "legend";
}

function toggleSecurity() {
  previousBasketApp.value = null; // Clear previous state on manual interaction
  activeBasketApp.value =
    activeBasketApp.value === "security" ? null : "security";
}

// Toggle route security alerts
function toggleRouteSecurityAlerts() {
  const routeApi = api || mapboxViewerRef.value;
  if (
    !routeApi ||
    !currentRouteStats.value ||
    !startHub.value ||
    !endHub.value
  ) {
    return;
  }

  routeSecurityAlertsActive.value = !routeSecurityAlertsActive.value;

  const routeId1 = Math.min(parseInt(startHub.value), parseInt(endHub.value));
  const routeId2 = Math.max(parseInt(startHub.value), parseInt(endHub.value));

  if (routeApi.toggleRouteSecurityAlerts) {
    routeApi.toggleRouteSecurityAlerts(
      routeId1,
      routeId2,
      routeSecurityAlertsActive.value
    );
  }
}

function handleUberImport() {
  if (!currentRouteStats.value || !startHub.value || !endHub.value) {
    return;
  }
  // Dummy function for Uber import
  console.log("Uber import clicked - route details would be imported here");
  // In a real implementation, this would open the Uber app or deep link
  // with the route details (start and end coordinates/addresses)
}

// Base URL for assets
const BASE = import.meta.env.BASE_URL || "/";

// Hover popup data
const popup = ref({ show: false, x: 0, y: 0, lights: 0, pois: 0, hub: "—" });

let api = null;
const mapboxViewerRef = ref(null);

// sidebar collapse state
const sidebarCollapsed = ref(true);
const sidebarWidth =
  ref(336); /* Default sidebar width - matches app basket width */
const sidebarHighlight = ref(false);
const isResizing = ref(false);
const isHovering = ref(false);
const showHistoryIndicator = ref(false);
const showRouteSavedMessage = ref(false);
const isFirstRouteCleared = ref(true);
const showWalkthrough = ref(false);
const routingHubsVisible = ref(true);
const showGuidedTour = ref(false);
const zurichFocusKey = ref(0);
const zurichFromButton = ref(false); // Flag to distinguish button click from walkthrough
const pendingTourAfterZoom = ref(false);
const mapReady = ref(false);
const showZurichReturnMessage = ref(false);

// Hover timer for opening collapsed sidebar
let hoverTimer = null;
const HOVER_DELAY = 800; // 800ms delay before opening
// Hover timer for closing expanded sidebar
let sidebarCloseTimer = null;
const SIDEBAR_CLOSE_DELAY = 800; // 800ms delay before closing

// Sidebar tab state - which section is currently active
const activeSidebarTab = ref("routing"); // "routing", "layers", "route-history", or "settings"

// Computed section title based on active tab
const sectionTitle = computed(() => {
  const titles = {
    routing: "Routing",
    layers: "Layers",
    "route-history": "Route History",
    settings: "Settings",
  };
  return titles[activeSidebarTab.value] || "Lumo Pro";
});

// Computed section hint/instruction text based on active tab
const sectionHint = computed(() => {
  const hints = {
    routing: "Select hubs to plan your route",
    layers: "Choose a layer to visualize on the map",
    "route-history": "View and reload your previous routes",
    settings: "Legal information, contact details, and help resources",
  };
  return hints[activeSidebarTab.value] || "";
});

// Section collapse states (kept for backward compatibility, but not used in new structure)
const routingCollapsed = ref(false);
const layersCollapsed = ref(false);
const legendCollapsed = ref(false);

// Layers section category expand/collapse states
const layersCategoryExpanded = ref(true);
const routingHubsCategoryExpanded = ref(true);
const routeHistoryExpanded = ref(true);

// Settings section category expand/collapse states
const imprintExpanded = ref(false);
const privacyExpanded = ref(false);
const termsExpanded = ref(false);
const aboutExpanded = ref(false);
const contactExpanded = ref(false);
const helpExpanded = ref(false);

// Settings categories configuration
const settingsCategories = [
  { id: "imprint", label: "Imprint" },
  { id: "privacy", label: "Privacy Policy" },
  { id: "terms", label: "Terms of Service" },
  { id: "about", label: "About" },
  { id: "contact", label: "Contact" },
  { id: "help", label: "Help / FAQ" },
];

// Get expanded state for a category
function getCategoryExpanded(categoryId) {
  const states = {
    imprint: imprintExpanded,
    privacy: privacyExpanded,
    terms: termsExpanded,
    about: aboutExpanded,
    contact: contactExpanded,
    help: helpExpanded,
  };
  return states[categoryId]?.value || false;
}

// Toggle category and scroll to it
function toggleAndScrollToCategory(categoryId) {
  const states = {
    imprint: imprintExpanded,
    privacy: privacyExpanded,
    terms: termsExpanded,
    about: aboutExpanded,
    contact: contactExpanded,
    help: helpExpanded,
  };

  const stateRef = states[categoryId];
  if (stateRef) {
    // Toggle the state
    stateRef.value = !stateRef.value;

    // If expanding, scroll to it after a short delay
    if (stateRef.value) {
      setTimeout(() => {
        const element = document.getElementById(`settings-${categoryId}`);
        if (element) {
          element.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }, 150);
    }
  }
}

// Map scale state
const mapZoom = ref(1.2);
const mapCenter = ref([0, 18]);
const scaleText = ref("1 km");
const locationText = ref("");
const zurichTime = ref("");
const isDaylight = ref(false);
const isTilted = ref(false);

// Greeting messages pool
const greetingMessages = [
  "Nice choice, John!",
  "Great pick, John!",
  "Solid route, John!",
  "Love this route, John!",
  "Perfect choice, John!",
  "Excellent selection, John!",
  "This looks awesome, John!",
  "You nailed it, John!",
  "Sweet route, John!",
  "This is fire, John!",
  "Brilliant choice, John!",
  "You've got great taste, John!",
  "This route's a winner, John!",
  "Spot on, John!",
  "Can't go wrong with this, John!",
];

const currentGreeting = ref("Nice choice, John!");

// Function to get a random greeting
function getRandomGreeting() {
  const randomIndex = Math.floor(Math.random() * greetingMessages.length);
  return greetingMessages[randomIndex];
}

// Update Zürich time
function updateZurichTime() {
  const now = new Date();

  // Determine if it's daylight hours (6 AM - 8 PM)
  const hour = now.getHours();
  isDaylight.value = hour >= 6 && hour < 20;
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: "Europe/Zurich",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  zurichTime.value = formatter.format(now);
}

// Set up time update interval
let timeInterval = null;

onMounted(() => {
  updateZurichTime();
  timeInterval = setInterval(updateZurichTime, 1000); // Update every second
});

onBeforeUnmount(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
});

// Calculate scale based on zoom level
function calculateScale(zoom, center) {
  // Reference: 120px on screen at current zoom
  const pixels = 120;
  const metersPerPixel =
    (156543.03392 * Math.cos((center[1] * Math.PI) / 180)) / Math.pow(2, zoom);
  const meters = metersPerPixel * pixels;

  // Format the scale text adaptively
  if (meters >= 1000) {
    const km = meters / 1000;
    if (km >= 10) {
      return `${Math.round(km)} km`;
    } else if (km >= 1) {
      return `${(Math.round(km * 10) / 10).toFixed(1)} km`;
    } else {
      return `${Math.round(meters)} m`;
    }
  } else if (meters >= 100) {
    return `${Math.round(meters / 50) * 50} m`;
  } else if (meters >= 10) {
    return `${Math.round(meters / 10) * 10} m`;
  } else {
    return `${Math.round(meters)} m`;
  }
}

function updateLocation(zoom) {
  // Simply show "Zürich" when zoomed in enough
  if (zoom >= 11.5) {
    locationText.value = "Zürich";
  } else {
    locationText.value = "";
  }
}

function handleMapZoom(event) {
  mapZoom.value = event.zoom;
  mapCenter.value = [event.center.lng, event.center.lat];
  scaleText.value = calculateScale(event.zoom, [
    event.center.lng,
    event.center.lat,
  ]);
  updateLocation(event.zoom);

  // Close app basket when zoomed out (same threshold as route fade: 11.5)
  const zoomThreshold = 11.5;
  if (event.zoom < zoomThreshold) {
    // Store current app state before closing
    if (activeBasketApp.value !== null) {
      previousBasketApp.value = activeBasketApp.value;
      activeBasketApp.value = null;
    }
  } else {
    // Restore previous app state when zoomed back in
    if (previousBasketApp.value !== null && activeBasketApp.value === null) {
      activeBasketApp.value = previousBasketApp.value;
      previousBasketApp.value = null;
    }
  }
}

function handleMapMove(event) {
  mapZoom.value = event.zoom;
  mapCenter.value = [event.center.lng, event.center.lat];
  scaleText.value = calculateScale(event.zoom, [
    event.center.lng,
    event.center.lat,
  ]);
  updateLocation(event.zoom);
}

// Scrollbar visibility
const scrollableRef = ref(null);
const chatScrollableRef = ref(null);
const isScrolling = ref(false);
let scrollTimeout = null;

function handleScroll() {
  // Show scrollbar immediately when scrolling
  isScrolling.value = true;

  // Clear existing timeout
  if (scrollTimeout) {
    clearTimeout(scrollTimeout);
  }

  // Hide scrollbar after scrolling stops (1s delay to match fade-out)
  scrollTimeout = setTimeout(() => {
    isScrolling.value = false;
    scrollTimeout = null;
  }, 1000);
}

onMounted(async () => {
  await nextTick();
  if (scrollableRef.value) {
    scrollableRef.value.addEventListener("scroll", handleScroll, {
      passive: true,
    });
    // Also listen for wheel events to catch mouse wheel scrolling
    scrollableRef.value.addEventListener("wheel", handleScroll, {
      passive: true,
    });
    // Listen for touch events on mobile
    scrollableRef.value.addEventListener("touchmove", handleScroll, {
      passive: true,
    });
  }
});

onBeforeUnmount(() => {
  if (scrollTimeout) {
    clearTimeout(scrollTimeout);
  }
  if (hoverTimer) {
    clearTimeout(hoverTimer);
  }
  if (sidebarCloseTimer) {
    clearTimeout(sidebarCloseTimer);
  }
  if (scrollableRef.value) {
    scrollableRef.value.removeEventListener("scroll", handleScroll);
    scrollableRef.value.removeEventListener("wheel", handleScroll);
    scrollableRef.value.removeEventListener("touchmove", handleScroll);
  }
});

// When Mapbox viewer is ready (will be implemented in MapboxViewer)
function onViewerReady(exposed) {
  api = exposed;
  if (api && api.onHover) {
    api.onHover((info) => {
      if (!info) {
        popup.value.show = false;
        return;
      }
      popup.value = { show: true, ...info };
    });
  }

  // Load hubs from the map component
  loadHubs();
}

// Load hubs from the map component
function loadHubs() {
  if (api && api.getHubs) {
    const loadedHubs = api.getHubs();
    console.log("Loaded hubs:", loadedHubs);
    if (loadedHubs && loadedHubs.length > 0) {
      hubs.value = loadedHubs;
      console.log("Hubs set in dropdown:", hubs.value);
    } else {
      console.warn("No hubs loaded from map component");
    }
  } else {
    console.warn("API or getHubs method not available");
  }
}

// Handle select blur - reset to collapsed state when dropdown closes
function handleSelectBlur() {
  // Reset to collapsed state (first 4 + "Show more") when dropdown closes
  // This ensures the dropdown always starts in collapsed state when reopened
  showAllHubs.value = false;
}

// Handle hub select change - detect "show more" click
function handleHubSelectChange(event, type) {
  const value = type === "start" ? startHub.value : endHub.value;

  // Check if "show_more" was selected
  if (value === "show_more") {
    // Show all hubs immediately - this will update displayedHubs computed property
    showAllHubs.value = true;

    // Reset the selection immediately
    if (type === "start") {
      startHub.value = "";
    } else {
      endHub.value = "";
    }

    // Use nextTick to ensure the DOM updates with new options, then try to reopen
    nextTick(() => {
      const selectRef =
        type === "start" ? startHubSelectRef.value : endHubSelectRef.value;
      if (selectRef) {
        // Try to reopen the dropdown by focusing and clicking
        // This works on some browsers but not all (native select limitation)
        selectRef.focus();
        setTimeout(() => {
          // Dispatch a mousedown event to simulate reopening
          const mouseEvent = new MouseEvent("mousedown", {
            bubbles: true,
            cancelable: true,
            view: window,
          });
          selectRef.dispatchEvent(mouseEvent);
          // Also try a click event
          selectRef.click();
        }, 5);
      }
    });
  }
}

// Handle hubs updated event (when locality names are fetched)
function handleHubsUpdated() {
  loadHubs();
}

// Handle hubs selected via map clicks
function handleHubsSelected({ hubId1, hubId2 }) {
  // Set flag to prevent watcher from triggering
  isHandlingHubClicks.value = true;

  // Update sidebar inputs to match the selected hubs
  startHub.value = hubId1;
  endHub.value = hubId2;

  // Set flag to prevent adding to history (route is already loaded on map)
  isLoadingFromHistory.value = true;

  // Update route stats and open chat app after a short delay
  setTimeout(() => {
    const routeApi = api || mapboxViewerRef.value;
    if (routeApi && routeApi.getCurrentRouteStats) {
      const stats = routeApi.getCurrentRouteStats();
      currentRouteStats.value = stats.current;
      fastRouteStats.value = stats.fast;
      brightRouteStats.value = stats.bright;
      console.log(
        "Updated route stats from hub clicks:",
        stats
      );
      // Automatically open chat app when route is created via hub clicks
      if (currentRouteStats.value) {
        previousBasketApp.value = null; // Clear previous state on programmatic open
        activeBasketApp.value = "chat";
      }
    }

    // Don't add to history here - routes are only added when cleared

    // Reset flags
    isLoadingFromHistory.value = false;
    isHandlingHubClicks.value = false;
  }, 800);
}

// Handle clear route button click
function handleClearRoute() {
  // Save route to history before clearing
  if (currentRouteStats.value && startHub.value && endHub.value) {
    const fromHub = displayedHubs.value.find((h) => h.id === startHub.value);
    const toHub = displayedHubs.value.find((h) => h.id === endHub.value);

    if (fromHub && toHub) {
      const historyEntry = {
        fromId: startHub.value,
        toId: endHub.value,
        fromName: fromHub.name,
        toName: toHub.name,
        date: new Date().toLocaleString("en-US", {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }),
        time: new Date().toLocaleString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      routeHistory.value.unshift(historyEntry);
      // Limit history to last 50 entries
      if (routeHistory.value.length > 50) {
        routeHistory.value = routeHistory.value.slice(0, 50);
      }

      // Show indicator for 3 seconds
      showHistoryIndicator.value = true;
      setTimeout(() => {
        showHistoryIndicator.value = false;
      }, 3000);

      // Show message at top center only for the first route cleared
      if (isFirstRouteCleared.value) {
        showRouteSavedMessage.value = true;
        isFirstRouteCleared.value = false;
      }
    }
  }

  // Clear route on map
  const routeApi = api || mapboxViewerRef.value;
  if (routeApi && routeApi.clearRoute) {
    routeApi.clearRoute();
  }

  // Reset selected hubs to ensure colors update back to grey
  if (routeApi && routeApi.selectHubs) {
    routeApi.selectHubs(null, null);
  }

  // Clear sidebar inputs
  startHub.value = "";
  endHub.value = "";

  // Clear route stats
  currentRouteStats.value = null;
  fastRouteStats.value = null;
  brightRouteStats.value = null;

  // Zoom to show all hubs after clearing route
  // Use setTimeout to ensure route clearing is complete
  if (routeApi && routeApi.zoomToAllHubs) {
    console.log("handleClearRoute: Will call zoomToAllHubs", {
      routeApi: !!routeApi,
      hasZoomToAllHubs: typeof routeApi.zoomToAllHubs === "function",
    });
    // Use a longer delay to ensure all clearing operations are complete
    setTimeout(() => {
      console.log("handleClearRoute: Executing zoomToAllHubs");
      try {
        routeApi.zoomToAllHubs();
      } catch (error) {
        console.error("handleClearRoute: Error calling zoomToAllHubs", error);
      }
    }, 300);
  } else {
    console.warn("handleClearRoute: zoomToAllHubs not available", {
      routeApi: !!routeApi,
      hasZoomToAllHubs: routeApi?.zoomToAllHubs ? true : false,
      routeApiKeys: routeApi ? Object.keys(routeApi) : [],
    });
  }

  // Close chat app if open
  if (activeBasketApp.value === "chat") {
    closeBasket();
  }
}

// Handle route popup click - toggle route details popup
function handlePolygonClicked(event) {
  // Toggle legend basket when a polygon is clicked
  if (activeBasketApp.value === "legend") {
    closeBasket();
  } else {
    previousBasketApp.value = null; // Clear previous state on programmatic open
    activeBasketApp.value = "legend";
  }
}

function handleRoutePopupClicked() {
  // If chat is open, close it; otherwise open chat
  if (activeBasketApp.value === "chat") {
    closeBasket();
  } else {
    previousBasketApp.value = null; // Clear previous state on programmatic open
    activeBasketApp.value = "chat";
  }
}

// Toggle route details popup (kept for backwards compatibility)
function toggleRouteDetailsPopup() {
  if (activeBasketApp.value === "chat") {
    closeBasket();
  } else {
    previousBasketApp.value = null; // Clear previous state on programmatic open
    activeBasketApp.value = "chat";
  }
}

// Toggle legend popup (kept for backwards compatibility)
function toggleLegendPopup() {
  if (activeBasketApp.value === "legend") {
    closeBasket();
  } else {
    previousBasketApp.value = null; // Clear previous state on programmatic open
    activeBasketApp.value = "legend";
  }
}

// Close route details popup (kept for backwards compatibility)
function closeRouteDetailsPopup() {
  activeBasketApp.value = null;
  userMessage.value = "";
  sentUserMessage.value = "";
  userMessageSent.value = false;
  showInput.value = false;
  messagesRouteKey.value = null;
}

// Open input box
const inputRef = ref(null);
function openInput() {
  showInput.value = true;
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus();
    }
  });
}

// Function to scroll chat to bottom
function scrollChatToBottom() {
  nextTick(() => {
    // Find the scrollable wrapper (parent of chatScrollableRef)
    const wrapper = chatScrollableRef.value?.parentElement;
    if (wrapper) {
      wrapper.scrollTo({
        top: wrapper.scrollHeight,
        behavior: "smooth",
      });
    }
  });
}

// Handle sending a message
function handleSendMessage() {
  const message = userMessage.value.trim();
  if (message && startHub.value && endHub.value) {
    // Store the route key for this message
    const routeKey = `${startHub.value}-${endHub.value}`;
    messagesRouteKey.value = routeKey;
    sentUserMessage.value = message;
    userMessageSent.value = true;
    userMessage.value = "";
    showInput.value = false;

    // Mark route as having shown responses (after animations complete)
    // The longest animation is safety bubble: 1.2s delay + 0.5s duration = 1.7s
    // Wait 2 seconds to ensure all animations complete
    if (!routesWithResponseShown.value.includes(routeKey)) {
      setTimeout(() => {
        if (!routesWithResponseShown.value.includes(routeKey)) {
          routesWithResponseShown.value.push(routeKey);
        }
      }, 2000);
    }

    // Scroll to bottom after message is sent
    scrollChatToBottom();
    // Also scroll after response appears (with delay for animation)
    setTimeout(() => {
      scrollChatToBottom();
    }, 500);
  }
}

// Computed property to check if route can be planned
const canPlanRoute = computed(() => {
  const canPlan =
    api && startHub.value && endHub.value && startHub.value !== endHub.value;
  console.log("canPlanRoute computed:", canPlan, {
    api: !!api,
    startHub: startHub.value,
    endHub: endHub.value,
  });
  return canPlan;
});

// Trigger routing between hubs
function route(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  // Ensure API is available - try to get it from ref if not set
  if (!api && mapboxViewerRef.value) {
    api = mapboxViewerRef.value;
  }

  console.log("🔵🔵🔵 route() function called 🔵🔵🔵");
  console.log("Current state:", {
    canPlanRoute: canPlanRoute.value,
    api: !!api,
    startHub: startHub.value,
    endHub: endHub.value,
    apiMethods: api ? Object.keys(api) : [],
    mapboxViewerRef: !!mapboxViewerRef.value,
  });

  // Always try to plan route, even if conditions aren't perfect
  if (!startHub.value || !endHub.value) {
    console.warn("⚠️ No hubs selected");
    alert("Please select both start and end hubs");
    return;
  }

  if (startHub.value === endHub.value) {
    console.warn("⚠️ Same hub selected for start and end");
    alert("Please select different hubs for start and end");
    return;
  }

  console.log("✅ Planning route from", startHub.value, "to", endHub.value);

  // Try to get API from ref if still not available
  const routeApi = api || mapboxViewerRef.value;

  if (routeApi && routeApi.selectHubs) {
    try {
      // Explicitly pass true to load the route
      console.log(
        "Calling routeApi.selectHubs with:",
        startHub.value,
        endHub.value,
        true
      );
      routeApi.selectHubs(startHub.value, endHub.value, true);
      console.log("✅ selectHubs called with loadRoute=true");

      // Update greeting with a random message
      currentGreeting.value = getRandomGreeting();

      // Update current route stats after a short delay to allow route to load
      setTimeout(() => {
        if (routeApi.getCurrentRouteStats) {
          const stats = routeApi.getCurrentRouteStats();
          currentRouteStats.value = stats.current;
          fastRouteStats.value = stats.fast;
          brightRouteStats.value = stats.bright;
          console.log("Updated route stats:", stats);
          // Automatically open chat app when route is created
          if (currentRouteStats.value) {
            previousBasketApp.value = null; // Clear previous state on programmatic open
            activeBasketApp.value = "chat";
          }
        }
      }, 800);

      // Add to history only if not loading from history
      if (!isLoadingFromHistory.value) {
        const fromHub = hubs.value.find((h) => h.id === startHub.value);
        const toHub = hubs.value.find((h) => h.id === endHub.value);
        if (fromHub && toHub) {
          // Don't add to history here - routes are only added when cleared
        }
      }

      // Update api reference for future use
      if (!api) {
        api = routeApi;
      }
    } catch (error) {
      console.error("❌ Error calling selectHubs:", error);
      alert("Error planning route: " + error.message);
    }
  } else {
    console.error("❌ API or selectHubs method not available", {
      api: api,
      routeApi: routeApi,
      hasSelectHubs: routeApi?.selectHubs,
      mapboxViewerRef: mapboxViewerRef.value,
      apiType: typeof api,
    });
    alert("Map not ready. Please wait a moment and try again.");
  }
}

// Watch for dropdown changes and automatically plan route when both are selected
watch(
  [startHub, endHub],
  ([newStart, newEnd], [oldStart, oldEnd]) => {
    // Skip if handling hub clicks (route is already loaded on map)
    if (isHandlingHubClicks.value) return;

    // Ignore "show_more" value - it's handled by handleHubSelectChange
    if (newStart === "show_more" || newEnd === "show_more") {
      return;
    }

    // Ensure API is available - try to get it from ref if not set
    if (!api && mapboxViewerRef.value) {
      api = mapboxViewerRef.value;
    }

    const routeApi = api || mapboxViewerRef.value;
    if (!routeApi || !routeApi.selectHubs) return;

    // Automatically plan route when both hubs are selected and different
    if (newStart && newEnd && newStart !== newEnd) {
      // Update greeting with a random message
      currentGreeting.value = getRandomGreeting();
      // Automatically plan the route - route() function will handle selectHubs, history, and stats
      route();
    }
    // If only start hub is selected, select it
    else if (newStart && !newEnd) {
      routeApi.selectHubs(newStart, null);
    }
    // If start hub is cleared, clear selection
    else if (!newStart) {
      routeApi.selectHubs(null, null);
      currentRouteStats.value = null; // Clear stats when route is cleared
      fastRouteStats.value = null;
      brightRouteStats.value = null;
    }

    // If both hubs are cleared, clear stats
    if (!newStart && !newEnd) {
      currentRouteStats.value = null;
      fastRouteStats.value = null;
      brightRouteStats.value = null;
    }

    // Update api reference for future use
    if (!api && routeApi) {
      api = routeApi;
    }
  },
  { immediate: false }
);

// Watch for route stats and automatically show popup when available
watch(
  currentRouteStats,
  (newStats, oldStats) => {
    if (newStats && Object.keys(newStats).length > 0) {
      // Automatically open chat app when route stats are available
      if (activeBasketApp.value !== "chat") {
        previousBasketApp.value = null; // Clear previous state on programmatic open
        activeBasketApp.value = "chat";
      }
      // If chat was already open, keep it open (elegant reload)
      // (already handled above)
      // Content will update automatically via reactivity
    } else {
      // Close popup when route stats are cleared
      routeDetailsPopupVisible.value = false;
    }
  },
  { deep: true }
);

// Watch for route changes and clear messages if route changed
watch([startHub, endHub], ([newStart, newEnd], [oldStart, oldEnd]) => {
  // If route changed (and both hubs are set), clear messages
  if (newStart && newEnd && (newStart !== oldStart || newEnd !== oldEnd)) {
    sentUserMessage.value = "";
    userMessageSent.value = false;
    messagesRouteKey.value = null;
    // Note: We don't clear routesWithResponseShown so responses appear instantly for routes that had responses before
  }
});

// Watch for chat app opening and mark route as shown (after animations complete)
watch(
  [activeBasketApp, startHub, endHub, currentRouteStats],
  (
    [newApp, newStart, newEnd, newStats],
    [oldApp, oldStart, oldEnd, oldStats]
  ) => {
    // Clear any pending timeout when route changes or chat closes
    if (markRouteShownTimeout) {
      clearTimeout(markRouteShownTimeout);
      markRouteShownTimeout = null;
    }

    // When chat app is opened and we have a route with stats
    if (
      newApp === "chat" &&
      newStart &&
      newEnd &&
      newStats &&
      Object.keys(newStats).length > 0
    ) {
      const routeKey = `${newStart}-${newEnd}`;

      // Only mark as shown if it hasn't been shown before
      // The longest animation is footer bubble: 1.3s delay + 0.5s duration = 1.8s
      // Wait 2.5 seconds to ensure all animations complete
      if (!routesShownInChat.value.includes(routeKey)) {
        markRouteShownTimeout = setTimeout(() => {
          // Add route key to array if not already present
          if (!routesShownInChat.value.includes(routeKey)) {
            routesShownInChat.value.push(routeKey);
          }
          markRouteShownTimeout = null;
        }, 2500);
      }
    }
  }
);

// Watch for messages and auto-scroll chat
watch(
  [userMessageSent, sentUserMessage, activeBasketApp],
  ([newSent, newMessage, newApp]) => {
    // Auto-scroll when message is sent or when chat is opened with existing messages
    if (newApp === "chat" && newSent && newMessage) {
      scrollChatToBottom();
      // Also scroll after a delay to catch response animations
      setTimeout(() => {
        scrollChatToBottom();
      }, 800);
    }
  }
);

// Watch for layer selection and automatically open legend app
watch(
  [lightingVisible, vibrancyVisible, combinedVisible],
  (
    [newLighting, newVibrancy, newCombined],
    [oldLighting, oldVibrancy, oldCombined]
  ) => {
    // If any layer is selected, open legend app
    if (newLighting || newVibrancy || newCombined) {
      previousBasketApp.value = null; // Clear previous state on programmatic open
      activeBasketApp.value = "legend";
    }
  },
  { immediate: false }
);

// Clear history
function clearHistory() {
  routeHistory.value = [];
}

// Format POI type for display
function formatPoiType(poiType) {
  const typeMap = {
    BarOrPub: "Bars & Pubs",
    CafeOrCoffeeShop: "Cafés",
    Restaurant: "Restaurants",
    NightClub: "Night Clubs",
    MusicVenue: "Music Venues",
  };
  return typeMap[poiType] || poiType;
}

// Format time only from date string
function formatTimeOnly(dateString) {
  if (!dateString) return "";
  // Extract time from date string (format: "Dec 6, 11:03 PM" -> "11:03 PM")
  // Handle both "Dec 6, 11:03 PM" and "Dec 6 at 11:03 PM" formats
  const match = dateString.match(/(\d{1,2}:\d{2}\s*(?:AM|PM))/i);
  return match ? match[1] : dateString;
}

// Get hub name from ID
function getHubName(hubId) {
  if (!hubId || !hubs.value) return "";
  const hub = hubs.value.find((h) => h.id === hubId);
  return hub ? hub.name : "";
}

// Get positive mantra for each POI type
function getPoiMantra(poiType) {
  const mantras = {
    BarOrPub: "Lively spots that keep the area active",
    CafeOrCoffeeShop: "Busy spots that add energy to your walk",
    Restaurant: "Well-frequented areas that stay active",
    NightClub: "Vibrant zones that stay well-lit",
    MusicVenue: "Cultural hotspots with regular events",
  };
  return mantras[poiType] || "Active points that make your route engaging";
}

// Get icon SVG for each POI type
function getPoiIcon(poiType) {
  const icons = {
    Restaurant: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/>
      <path d="M7 2v20"/>
      <path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3z"/>
      <path d="M21 15v7"/>
      <path d="M8 22h8"/>
    </svg>`,
    BarOrPub: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M9 2v20M15 2v20"/>
      <path d="M2 2h20"/>
      <path d="M2 6h20"/>
      <path d="M2 10h20"/>
      <path d="M2 14h20"/>
      <path d="M2 18h20"/>
      <path d="M2 22h20"/>
    </svg>`,
    CafeOrCoffeeShop: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M18 8h1a4 4 0 0 1 0 8h-1"/>
      <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>
      <line x1="6" y1="1" x2="6" y2="4"/>
      <line x1="10" y1="1" x2="10" y2="4"/>
      <line x1="14" y1="1" x2="14" y2="4"/>
      <circle cx="12" cy="12" r="1" fill="currentColor"/>
    </svg>`,
    MusicVenue: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="18" cy="16" r="3"/>
      <circle cx="6" cy="16" r="3"/>
      <path d="M18 13V7a4 4 0 0 0-4-4H10a4 4 0 0 0-4 4v6"/>
      <path d="M6 13v3"/>
      <path d="M18 13v3"/>
      <path d="M9 9h6"/>
    </svg>`,
    NightClub: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="6"/>
      <circle cx="12" cy="12" r="2"/>
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
    </svg>`,
  };

  return icons[poiType] || icons.Restaurant;
}

// Format POI frequency as "A [type] every [time]"
function formatPoiFrequency(poiType, frequency) {
  if (!frequency) return "";

  // Get singular form of POI type
  const singularMap = {
    BarOrPub: "bar",
    CafeOrCoffeeShop: "café",
    Restaurant: "restaurant",
    NightClub: "night club",
    MusicVenue: "music venue",
  };

  const singularType = singularMap[poiType] || "point of interest";

  // Format as "A restaurant every 30 seconds"
  return `A ${singularType} every ${frequency}`;
}

// Extract time part from frequency string (e.g., "every 3 min" -> "3 min")
function extractTimeFromFrequency(freq) {
  if (!freq) return "";
  // Remove "every " prefix if present
  return freq.replace(/^every\s+/i, "").trim();
}

// Get formatted route introduction text
function getRouteIntroText() {
  if (!currentRouteStats.value || !startHub.value || !endHub.value) {
    return "";
  }

  const stats = currentRouteStats.value;
  let routeDescription = "";

  // Get route description based on POI density - concise and positive
  if (stats.poiCounts) {
    const totalPois = Object.values(stats.poiCounts).reduce(
      (sum, count) => sum + count,
      0
    );
    if (totalPois > 50) {
      routeDescription =
        "route buzzing with life - cozy cafes, great restaurants, and lively spots await";
    } else if (totalPois > 20) {
      routeDescription =
        "route full of activity - you'll feel safe and connected to the city's energy";
    } else if (totalPois > 0) {
      routeDescription =
        "peaceful route with just the right balance - calm yet engaging";
    } else {
      routeDescription = "serene path perfect for a relaxing walk";
    }
  } else if (stats.lumoScore !== null && stats.lumoScore > 70) {
    routeDescription = "well-lit, active route - safe and vibrant";
  } else {
    routeDescription = "route that balances everything for a great walk";
  }

  return `Here's what makes this route special: ${routeDescription}.`;
}

// Get one most relevant tip based on route stats
function getRouteTips() {
  if (!currentRouteStats.value) return [];

  const stats = currentRouteStats.value;
  const tips = [];

  // Only POI-based tips, no duration tips
  if (stats.poiCounts) {
    const totalPois = Object.values(stats.poiCounts).reduce(
      (sum, count) => sum + count,
      0
    );
    if (totalPois > 50) {
      tips.push("Lots of cafes and restaurants along the way");
      return tips; // Return early with most relevant tip
    } else if (totalPois < 10) {
      tips.push("Quieter, peaceful route");
      return tips;
    }
  }

  return tips.slice(0, 1); // Only return one tip
}

// Load route from history
function loadHistoryRoute(entry) {
  // Set flag to prevent adding this route to history
  isLoadingFromHistory.value = true;

  startHub.value = entry.fromId;
  endHub.value = entry.toId;
  // Trigger route loading
  const routeApi = api || mapboxViewerRef.value;
  if (routeApi && routeApi.selectHubs) {
    routeApi.selectHubs(entry.fromId, entry.toId, true);
    // Update greeting with a random message
    currentGreeting.value = getRandomGreeting();
    // Update current route stats after a short delay
    setTimeout(() => {
      if (routeApi.getCurrentRouteStats) {
        const stats = routeApi.getCurrentRouteStats();
        currentRouteStats.value = stats.current;
        fastRouteStats.value = stats.fast;
        brightRouteStats.value = stats.bright;
        console.log(
          "Updated route stats from history:",
          stats
        );
        // Automatically open chat app when route is loaded from history
        if (currentRouteStats.value) {
          previousBasketApp.value = null; // Clear previous state on programmatic open
          activeBasketApp.value = "chat";
        }
      }
      // Reset flag after route is loaded
      isLoadingFromHistory.value = false;
    }, 800);
  } else {
    // Reset flag if API is not available
    isLoadingFromHistory.value = false;
  }
}

// Swap hubs function
function swapHubs() {
  const a = startHub.value;
  startHub.value = endHub.value;
  endHub.value = a;
}

function toggleRoutingHubs() {
  routingHubsVisible.value = !routingHubsVisible.value;
}

function startTour() {
  showWalkthrough.value = false;
  pendingTourAfterZoom.value = true;
}

function finishTour() {
  showGuidedTour.value = false;
}

// Map control handlers
function handleZoomIn() {
  if (mapboxViewerRef.value && mapboxViewerRef.value.zoomIn) {
    mapboxViewerRef.value.zoomIn();
  }
}

function handleZoomOut() {
  if (mapboxViewerRef.value && mapboxViewerRef.value.zoomOut) {
    mapboxViewerRef.value.zoomOut();
  }
}

function handleResetNorth() {
  if (mapboxViewerRef.value && mapboxViewerRef.value.resetNorth) {
    mapboxViewerRef.value.resetNorth();
  }
}

function handleToggleFullscreen() {
  if (mapboxViewerRef.value && mapboxViewerRef.value.toggleFullscreen) {
    mapboxViewerRef.value.toggleFullscreen();
  }
}

function handleToggleTilt() {
  if (mapboxViewerRef.value && mapboxViewerRef.value.toggleTilt) {
    mapboxViewerRef.value.toggleTilt();
    // Update isTilted state from the viewer
    if (mapboxViewerRef.value.getIsTilted) {
      isTilted.value = mapboxViewerRef.value.getIsTilted();
    }
  }
}

// Watch for tilt changes from the map
watch(
  () => mapboxViewerRef.value?.getIsTilted?.(),
  (newValue) => {
    if (newValue !== undefined) {
      isTilted.value = newValue;
    }
  }
);

function focusZurich(fromButton = false) {
  zurichFromButton.value = fromButton; // Set flag before triggering zoom
  zurichFocusKey.value = Date.now();
  showZurichReturnMessage.value = false; // Hide the message when zooming to Zurich
}

function handleGoBackToZurich() {
  focusZurich(true);
}

// Check if user is zoomed out of Zurich
const isOutOfZurich = computed(() => {
  if (!mapCenter.value || mapZoom.value === undefined || !mapReady.value)
    return false;

  // Zurich center coordinates
  const zurichCenter = [8.55, 47.37];
  const currentCenter = mapCenter.value;

  // Calculate distance in degrees (rough approximation)
  const latDiff = Math.abs(currentCenter[1] - zurichCenter[1]);
  const lonDiff = Math.abs(currentCenter[0] - zurichCenter[0]);
  const distance = Math.sqrt(latDiff * latDiff + lonDiff * lonDiff);

  // Show message if zoomed out too far (zoom < 10) or moved far from Zurich center (> 0.1 degrees ≈ 11km)
  return mapZoom.value < 10 || distance > 0.1;
});

// Watch for changes in zoom/center to show/hide the message
watch(
  [isOutOfZurich, mapReady],
  ([outOfZurich, ready]) => {
    if (ready && outOfZurich && !showRouteSavedMessage.value) {
      showZurichReturnMessage.value = true;
    } else if (!outOfZurich) {
      showZurichReturnMessage.value = false;
    }
  },
  { immediate: true }
);

function handleHotspotClick(hotspot) {
  if (api && api.zoomToCoordinates && hotspot.lon && hotspot.lat) {
    // Use higher zoom for vibrancy hotspots to show POI points
    const zoomLevel = hotspot.layerType === "vibrancy" ? 16 : 15;
    api.zoomToCoordinates(hotspot.lon, hotspot.lat, zoomLevel);

    // Display hotspot name
    if (hotspot.name) {
      // Clear any existing timeout
      if (hotspotNameTimeout) {
        clearTimeout(hotspotNameTimeout);
        hotspotNameTimeout = null;
      }

      // Set the hotspot name
      displayedHotspotName.value = hotspot.name;

      // Clear after 4 seconds
      hotspotNameTimeout = setTimeout(() => {
        displayedHotspotName.value = null;
        hotspotNameTimeout = null;
      }, 4000);
    }
  }
}

function handleMapReady() {
  mapReady.value = true;
  // Try to get API from ref if not already set
  if (!api && mapboxViewerRef.value) {
    api = mapboxViewerRef.value;
    loadHubs();
  } else if (api) {
    // If API is already set, try loading hubs again
    loadHubs();
  }
  // Automatically open chat basket right after routing hub labels appear
  // Hub labels appear at 1.1s and finish at ~1.5s, so open chat basket after that
  setTimeout(() => {
    activeBasketApp.value = "chat";
  }, 1600);
}

function handleZurichZoomComplete() {
  if (!pendingTourAfterZoom.value) return;
  showGuidedTour.value = true;
  pendingTourAfterZoom.value = false;
}

// Handle toggle button click - toggle sidebar with smooth transition
function handleToggleSidebar() {
  // Clear any hover timer
  if (hoverTimer) {
    clearTimeout(hoverTimer);
    hoverTimer = null;
  }

  // Toggle sidebar (transition will handle the smooth animation)
  sidebarCollapsed.value = !sidebarCollapsed.value;
}

// Handle sidebar mouse enter - start hover timer if collapsed
function handleSidebarMouseEnter() {
  isHovering.value = true;

  // If sidebar is collapsed, start timer to open it
  if (sidebarCollapsed.value) {
    // Clear any existing timer
    if (hoverTimer) {
      clearTimeout(hoverTimer);
    }

    // Start new timer
    hoverTimer = setTimeout(() => {
      if (sidebarCollapsed.value && isHovering.value) {
        sidebarCollapsed.value = false;
      }
      hoverTimer = null;
    }, HOVER_DELAY);
  }
}

// Handle sidebar mouse leave - clear hover timer
function handleMouseLeave() {
  isHovering.value = false;

  // Clear hover timer if it exists
  if (hoverTimer) {
    clearTimeout(hoverTimer);
    hoverTimer = null;
  }
}

// Handle sidebar toggle button hover - close if expanded
function handleSidebarToggleHover() {
  // Only close if sidebar is expanded (not collapsed)
  if (!sidebarCollapsed.value) {
    // Clear any existing timer
    if (sidebarCloseTimer) {
      clearTimeout(sidebarCloseTimer);
    }

    // Start timer to close
    sidebarCloseTimer = setTimeout(() => {
      if (!sidebarCollapsed.value) {
        sidebarCollapsed.value = true;
      }
      sidebarCloseTimer = null;
    }, SIDEBAR_CLOSE_DELAY);
  }
}

// Handle sidebar toggle button leave - clear close timer
function handleSidebarToggleLeave() {
  if (sidebarCloseTimer) {
    clearTimeout(sidebarCloseTimer);
    sidebarCloseTimer = null;
  }
}

// Handle icon click - open sidebar if collapsed and set the active tab
function handleIconClick(tab) {
  // If sidebar is collapsed, open it immediately
  if (sidebarCollapsed.value) {
    // Clear any hover timer
    if (hoverTimer) {
      clearTimeout(hoverTimer);
      hoverTimer = null;
    }
    // For layers section, delay showing content until sidebar animation completes
    if (tab === "layers") {
      activeSidebarTab.value = ""; // Clear active tab first to prevent flicker
      // Open sidebar
      sidebarCollapsed.value = false;
      // Delay showing layers content until sidebar expansion animation completes
      // Use nextTick to ensure DOM update, then wait for transition
      nextTick(() => {
        setTimeout(() => {
          activeSidebarTab.value = tab;
        }, 400); // Match sidebar transition duration (0.4s)
      });
    } else {
      // Open sidebar instantly
      sidebarCollapsed.value = false;
      // Set the active tab immediately for other sections
      activeSidebarTab.value = tab;
    }
  } else {
    // Sidebar already open
    // If clicking on the same tab that's currently active, collapse the sidebar
    if (activeSidebarTab.value === tab) {
      sidebarCollapsed.value = true;
    } else {
      // If clicking on a different tab, switch to it and keep sidebar open
      activeSidebarTab.value = tab;
    }
  }
}

function handleOpenLayersSection() {
  // Check if layers section is already open
  if (activeSidebarTab.value === "layers" && !sidebarCollapsed.value) {
    // Add visual feedback by brightening the sidebar
    sidebarHighlight.value = true;
    setTimeout(() => {
      sidebarHighlight.value = false;
    }, 300); // Quick highlight animation
  }
  handleIconClick("layers");
}

function handleMapClicked() {
  // Close sidebar instantly when map is clicked
  closeSidebarInstantly();
}

function handleAppClick(e) {
  // Close sidebar if clicking outside of it
  // Check if click is outside the sidebar
  const sidebar = e.target.closest(".sidebar");
  const appBasket = e.target.closest(".app-basket");
  // Don't close if clicking on sidebar or app basket
  if (!sidebar && !appBasket && !sidebarCollapsed.value) {
    closeSidebarInstantly();
  }
}

function closeSidebarInstantly() {
  // Close sidebar instantly (if not already collapsed)
  if (!sidebarCollapsed.value) {
    // Clear any hover or close timers
    if (hoverTimer) {
      clearTimeout(hoverTimer);
      hoverTimer = null;
    }
    if (sidebarCloseTimer) {
      clearTimeout(sidebarCloseTimer);
      sidebarCloseTimer = null;
    }
    // Close instantly
    sidebarCollapsed.value = true;
  }
}

function openHistorySection() {
  // Close the message
  showRouteSavedMessage.value = false;
  // Open sidebar if collapsed
  if (sidebarCollapsed.value) {
    sidebarCollapsed.value = false;
  }
  // Switch to history tab
  handleIconClick("route-history");
}

function handleOpenRoutingTool() {
  // Clear any hover timers that might interfere
  if (hoverTimer) {
    clearTimeout(hoverTimer);
    hoverTimer = null;
  }
  // handleIconClick already handles opening sidebar if collapsed and switching tabs
  handleIconClick("routing");
}

// Handle sidebar click - open if collapsed (unless clicking on button or resize handle)
function handleSidebarClick(e) {
  // Only open if collapsed
  if (!sidebarCollapsed.value) return;

  // Don't open if clicking on the toggle button (let button handle its own click)
  if (e.target.closest(".sidebar-toggle")) return;

  // Don't open if clicking on the resize handle
  if (e.target.closest(".sidebar-resize-handle")) return;

  // Don't open if clicking on icon bar buttons
  if (e.target.closest(".sidebar-icon-bar")) return;

  // Clear hover timer since we're opening via click
  if (hoverTimer) {
    clearTimeout(hoverTimer);
    hoverTimer = null;
  }

  // Open the sidebar
  sidebarCollapsed.value = false;
}

// Sidebar resize functionality
function startResize(e) {
  e.preventDefault();
  const startX = e.clientX;
  const startWidth = sidebarWidth.value;

  function handleMouseMove(e) {
    const diff = e.clientX - startX;
    const newWidth = Math.max(240, Math.min(600, startWidth + diff));
    sidebarWidth.value = newWidth;
  }

  function handleMouseUp() {
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
    isResizing.value = false;
  }

  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("mouseup", handleMouseUp);
  isResizing.value = true;
}
</script>

<style>
/* -------- GLOBAL LAYOUT -------- */
html,
body,
#app {
  height: 100%;
  margin: 0;
  background: #0b0b0c;
  color: #eaeaea;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.app {
  position: relative;
  height: 100%;
  overflow: hidden;
}

/* Top Center Buttons Container */
.top-center-buttons-container {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.top-center-buttons-container--zurich-message-visible {
  top: 82px; /* Move down when Zurich message is visible (30px + 52px for message height + gap) */
}

/* Clear Route Button (Top Center) */
.clear-route-top-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  background: rgba(26, 27, 30, 0.15);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: none;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  white-space: nowrap;
}

.clear-route-top-button:hover {
  background: rgba(26, 27, 30, 0.6);
  color: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.clear-route-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    transform 0.15s ease;
  flex-shrink: 0;
}

.clear-route-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

.clear-route-close:active {
  transform: scale(0.95);
}

.clear-route-close svg {
  flex-shrink: 0;
}

.clear-route-icon {
  flex-shrink: 0;
  color: inherit;
  opacity: 0.3;
  transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.clear-route-top-button:hover .clear-route-icon {
  opacity: 1;
}

/* Active Layer Indicator Button */
.active-layer-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  background: rgba(26, 27, 30, 0.15);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: none;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.01em;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition:
    background 0.2s ease,
    color 0.2s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
  white-space: nowrap;
}

.active-layer-name {
  flex-shrink: 0;
  white-space: nowrap;
}

.active-layer-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    transform 0.15s ease;
  flex-shrink: 0;
}

.active-layer-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

.active-layer-close:active {
  transform: scale(0.95);
}

.active-layer-close svg {
  flex-shrink: 0;
}

.active-layer-icon {
  flex-shrink: 0;
  color: inherit;
  opacity: 0.7;
}

.active-layer-button:hover {
  background: rgba(26, 27, 30, 0.6);
  color: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.active-layer-button:active {
  transform: translateY(0);
}

/* Hotspot Name Pop-up */
.hotspot-name-popup {
  position: fixed;
  top: 90px; /* Positioned under the top-center-buttons-container */
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  font-size: 32px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.02em;
  text-align: center;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  user-select: none;
}

/* Hotspot Name Animation */
.hotspot-name-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.hotspot-name-fade-leave-active {
  transition: all 0.35s cubic-bezier(0.55, 0.06, 0.68, 0.19);
}

.hotspot-name-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px) scale(0.95);
}

.hotspot-name-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px) scale(0.95);
}

/* Remove blue focus outlines globally */
*:focus,
*:focus-visible,
*:focus-within {
  outline: none !important;
  box-shadow: none !important;
}

button:focus,
button:focus-visible,
input:focus,
input:focus-visible,
select:focus,
select:focus-visible,
textarea:focus,
textarea:focus-visible {
  outline: none !important;
  box-shadow: none !important;
  border-color: transparent !important;
}

/* -------- SIDEBAR -------- */
.sidebar {
  position: absolute;
  top: 30px;
  left: 30px;
  bottom: 30px;
  width: 336px; /* Default sidebar width - matches app basket width */
  padding: 0;
  background: #151517;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  z-index: 10;
  border-radius: 16px;
  transition: background-color 0.3s ease;
}

.sidebar--highlight {
  background: #1f1f22;
}

.sidebar:not(.sidebar--collapsed) {
  background: rgba(21, 21, 23, 0.75);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);

  display: flex;
  flex-direction: row; /* Changed to row to accommodate icon bar */
  justify-content: flex-start;

  transition:
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease;
}

.sidebar:not(.sidebar--collapsed).sidebar--highlight {
  background: rgba(35, 35, 38, 0.85);
}

/* Sidebar main content wrapper */
.sidebar-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px 16px 16px 20px;
  min-width: 0; /* Allow flex shrinking */
  overflow: visible; /* Allow profile avatar to extend beyond bounds */
  opacity: 1;
  transform: translateX(0);
  visibility: visible;
  transition:
    opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0s,
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0s,
    visibility 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0s;
}

/* Hide sidebar-main content when collapsed */
.sidebar--collapsed .sidebar-main {
  display: flex; /* Keep flex layout for transitions */
  opacity: 0;
  transform: translateX(-10px); /* Slight slide-in effect */
  pointer-events: none;
  visibility: hidden; /* Hide but allow transitions */
  transition:
    opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    visibility 0.3s cubic-bezier(0.4, 0, 0.2, 1); /* Faster fade-out */
}

/* Resize handle */
.sidebar-resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  z-index: 11;
  background: transparent;
  transition: background-color 0.2s ease;
}

.sidebar-resize-handle:hover,
.sidebar-resize-handle:active {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar--collapsed .sidebar-resize-handle {
  display: none;
}

/* Ensure button and resize handle keep their own cursors */
.sidebar--collapsed .sidebar-toggle {
  cursor: e-resize;
}

.sidebar--collapsed .sidebar-resize-handle {
  cursor: col-resize;
}

/* Sidebar Icon Bar (VS Code style) */
.sidebar-icon-bar {
  width: 64px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  gap: 4px;
  background: #1a1b1e;
  border-radius: 16px 0 0 16px;
  flex-shrink: 0;
  justify-content: space-between;
  position: relative; /* Ensure it stays in place */
}

.sidebar-icon-bar-top {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
  justify-content: flex-start; /* Align buttons at top */
  width: 100%;
  padding-top: 90px; /* Match collapsed sidebar exactly: collapsed routing button at 8px + 12px + 40px + 4px + 34px = 98px, so opened needs 8px + 90px = 98px */
  position: relative; /* Allow absolute positioning of logo */
}

.sidebar-icon-btn {
  position: relative;
  width: 40px;
  height: 40px;
  border: none;
  background: transparent !important; /* Transparent to adapt to bar color - override global button style */
  background-color: transparent !important; /* Ensure background-color is also transparent */
  color: rgba(255, 255, 255, 0.4); /* Default color */
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.15s ease;
  padding: 0;
  position: relative;
  box-sizing: border-box;
}

/* Opened sidebar: make icons more transparent - no transition to prevent flash */
.sidebar:not(.sidebar--collapsed) .sidebar-icon-btn:not(.active) {
  color: rgba(
    255,
    255,
    255,
    0.25
  ) !important; /* More transparent for opened sidebar */
  transition: none !important; /* No transition to prevent flash */
}

/* Opened sidebar: hover state more transparent (but not for active) */
.sidebar:not(.sidebar--collapsed) .sidebar-icon-btn:not(.active):hover {
  background: transparent !important; /* Transparent to adapt to bar color */
  background-color: transparent !important;
  color: rgba(
    255,
    255,
    255,
    0.5
  ) !important; /* Slightly more visible on hover, but still transparent */
}

.sidebar-icon-btn:hover {
  background: transparent !important; /* Transparent to adapt to bar color */
  background-color: transparent !important;
  color: #ffffff; /* SVG turns white on hover */
}

/* History Indicator */
.history-indicator {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  background: #60a5fa;
  border-radius: 50%;
  border: 1.5px solid #1a1b1e;
  z-index: 10;
  animation: historyIndicatorPulse 0.3s ease-out;
  box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.3);
}

@keyframes historyIndicatorPulse {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Route Saved Message */
.route-saved-message {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: rgba(26, 27, 30, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: none;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  animation: routeSavedMessageAppear 0.3s ease-out;
}

@keyframes routeSavedMessageAppear {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.route-saved-text {
  white-space: nowrap;
}

.route-saved-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.route-saved-button {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.route-saved-button--close {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.route-saved-button--close:hover {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

.route-saved-button--open {
  background: #ffffff;
  color: #000000;
}

.route-saved-button--open:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #000000;
}

/* Go Back to Zurich Message */
.zurich-return-message {
  position: absolute;
  top: 30px; /* Same position as top-center-buttons-container */
  left: 50%;
  transform: translateX(-50%);
  z-index: 101; /* Above route-saved-message and top-center-buttons */
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: rgba(26, 27, 30, 0.4);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: none;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.zurich-return-text {
  white-space: nowrap;
}

.zurich-return-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zurich-return-button {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zurich-return-button--yes {
  background: #ffffff;
  color: #000000;
}

.zurich-return-button--yes:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #000000;
}

.zurich-return-button--close {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
}

.zurich-return-button--close:hover {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

/* Zurich Return Message Animation */
.zurich-return-fade-enter-active {
  transition: all 0.3s ease-out;
}

.zurich-return-fade-leave-active {
  transition: all 0.3s ease-in;
}

.zurich-return-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

.zurich-return-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

/* Override hover for opened sidebar non-active icons */
.sidebar:not(.sidebar--collapsed) .sidebar-icon-btn:not(.active):hover {
  color: rgba(255, 255, 255, 0.5) !important; /* Override general hover rule */
}

.sidebar-icon-btn.active {
  background: transparent !important; /* Transparent to adapt to bar color */
  background-color: transparent !important;
  color: #ffffff !important; /* True white when active - always full white */
}

.sidebar-icon-btn.active::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 28px;
  background: #ffffff;
  border-radius: 0;
  opacity: 1;
}

/* Sidebar icon bar bottom section (for settings above profile) */
.sidebar-icon-bar-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: absolute;
  bottom: 82px; /* Avatar is at bottom: 22px, avatar height 30px, so 22px + 30px + 30px spacing = 82px */
  left: 0;
  right: 0;
  z-index: 12; /* Above the avatar (z-index: 11) */
}

.sidebar-icon-btn img,
.sidebar-icon-btn svg {
  width: 20px;
  height: 20px;
  display: block;
}

/* Make dark SVG icons white/visible for sidebar */
.sidebar-icon-btn img {
  filter: brightness(0) invert(1);
}

/* Opened sidebar: make img icons more transparent (for routing, layers) */
.sidebar:not(.sidebar--collapsed) .sidebar-icon-btn:not(.active) img {
  opacity: 0.25 !important; /* Match the transparency of SVG icons */
  transition: none !important; /* No transition to prevent flash */
}

/* Opened sidebar: hover state for img icons */
.sidebar:not(.sidebar--collapsed) .sidebar-icon-btn:not(.active):hover img {
  opacity: 0.5 !important; /* Match the hover transparency of SVG icons */
}

/* Active img icons should be fully opaque */
.sidebar-icon-btn.active img {
  opacity: 1 !important;
}

.sidebar-icon-btn svg {
  stroke: currentColor;
  fill: none;
}

.sidebar-icon-tooltip {
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: #ffffff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0ms,
    visibility 0ms;
  z-index: 10000;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
}

.sidebar-icon-btn:hover .sidebar-icon-tooltip {
  opacity: 1;
  visibility: visible;
  transition:
    opacity 0ms,
    visibility 0ms;
}

/* Divider line between icon bar and content */
.sidebar-divider {
  display: none; /* Hide the vertical divider line */
}

/* Lumo logo in icon bar when opened - positioned where collapsed toggle button is */
.sidebar-logo {
  position: absolute;
  top: 20px; /* Align with Lumo Pro text: sidebar-main padding-top (20px) - logo should align with text baseline */
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.sidebar-logo-icon {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

/* Collapsed sidebar icon bar - width is set in .sidebar--collapsed .sidebar-icon-bar below */

.sidebar--collapsed .sidebar-icon-bar-top {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  justify-content: flex-start; /* Position buttons at the top */
  flex: 0 0 auto; /* Don't take all space, keep buttons at top */
  padding-top: 12px; /* Align with close button in opened sidebar (8px icon-bar padding + 12px = 20px total) */
}

.sidebar--collapsed .sidebar-icon-btn {
  width: 40px;
  height: 40px; /* Quadratic (square) */
}

.sidebar--collapsed .sidebar-icon-btn.active::before {
  display: none; /* Hide active indicator when collapsed */
}

.sidebar--collapsed .sidebar-icon-btn img,
.sidebar--collapsed .sidebar-icon-btn svg {
  width: 20px;
  height: 20px;
}

/* Make other buttons transparent in collapsed sidebar (except the toggle button) */
.sidebar--collapsed .sidebar-icon-btn:not(.sidebar-toggle-icon-btn) {
  opacity: 0.3;
}

.sidebar--collapsed .sidebar-icon-btn:not(.sidebar-toggle-icon-btn):hover {
  opacity: 0.5;
}

/* Style the open sidebar button in collapsed sidebar to match close button exactly */
.sidebar--collapsed .sidebar-toggle-icon-btn {
  width: 30px !important;
  height: 30px !important;
  background: transparent !important;
  background-color: transparent !important;
  border-radius: 8px;
  cursor: e-resize !important; /* Arrow pointing right */
  display: grid !important;
  place-items: center !important;
  box-sizing: border-box !important;
  padding: 0 !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: #e6e6e8 !important;
}

.sidebar--collapsed .sidebar-toggle-icon-btn:hover {
  background: #2a2f34 !important;
  background-color: #2a2f34 !important;
}

.sidebar--collapsed .sidebar-toggle-icon-btn:active {
  background: #1c1e21 !important;
  background-color: #1c1e21 !important;
}

/* Make the icon in collapsed sidebar toggle button same size as close button */
.sidebar--collapsed .sidebar-toggle-icon-btn .sidebar-toggle-icon {
  width: 18px !important;
  height: 18px !important;
}

/* Position tooltip below the toggle button in collapsed sidebar (like close button) */
.sidebar--collapsed .sidebar-toggle-icon-btn .sidebar-icon-tooltip {
  left: 50%;
  top: calc(100% + 8px);
  transform: translateX(-50%);
}

/* Make all SVG icons white when hovering on collapsed sidebar */
.sidebar--collapsed:hover .sidebar-icon-btn {
  color: #ffffff !important;
}

/* Push routing, layers, and statistics buttons down to align with Routing Hubs button */
.sidebar--collapsed
  .sidebar-icon-bar-top
  .sidebar-icon-btn.sidebar-toggle-icon-btn
  + .sidebar-icon-btn {
  margin-top: 34px !important; /* Align routing button with Routing Hubs button: 98px (Routing Hubs) - 64px (current position) = 34px */
}

/* Scrollable content area */
.sidebar-scrollable {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  margin-right: -16px;
  padding-right: 16px;
  margin-top: 24px; /* Coherent space below section header across all sections */
  opacity: 1;
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.15s; /* Smooth fade-in with slight delay */
}

/* Fade out scrollable when collapsed */
.sidebar--collapsed .sidebar-scrollable {
  opacity: 0;
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1); /* Faster fade-out */
}

/* Scrollbar - only visible when scrolling */
.sidebar-scrollable::-webkit-scrollbar {
  width: 14px;
}

.sidebar-scrollable::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-scrollable::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 7px;
  opacity: 0;
  transition: opacity 1s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.sidebar-scrollable--scrolling::-webkit-scrollbar-thumb {
  opacity: 1;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-scrollable--scrolling::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Firefox */
.sidebar-scrollable {
  scrollbar-width: none;
}

.sidebar-scrollable--scrolling {
  scrollbar-width: auto;
  scrollbar-color: rgba(255, 255, 255, 0.4) transparent;
}

.sidebar h2 {
  margin: 6px 0 0 0;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.sidebar h2 .muted {
  color: #b9b9c0;
  font-weight: 600;
}
.nowrap {
  white-space: nowrap;
}

.sidebar .group {
  margin-top: 18px;
}

.sidebar-routing {
  position: relative;
  padding-top: 0;
  margin-top: 0; /* Spacing is now handled by sidebar-scrollable */
}

.sidebar .title {
  color: #b8bcc0;
  font-size: 14px;
  letter-spacing: 0.02em;
  margin-bottom: 16px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.title-collapsible {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
}

.chevron {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
  line-height: 1;
  flex-shrink: 0;
  display: inline-block;
  transform: scaleY(1.3);
  opacity: 0;
}

.chevron-category {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  transform: rotate(0deg);
  opacity: 0;
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
  margin-left: 2px;
  display: inline-block;
  line-height: 1;
  vertical-align: baseline;
  position: relative;
  top: 1px;
}

/* Only show chevron when its specific category is hovered */
.layers-category:hover > .title-collapsible .chevron-category {
  opacity: 1;
}

/* Ensure chevrons in non-hovered categories stay hidden */
.layers-category:not(:hover) > .title-collapsible .chevron-category {
  opacity: 0 !important;
}

.group:hover .chevron {
  opacity: 1;
}

.chevron--expanded {
  transform: scaleX(1.3) rotate(90deg);
}

.chevron-category.chevron--expanded {
  transform: rotate(90deg);
}

.section-content {
  overflow: visible;
  max-height: none;
  transition: opacity 0.2s ease;
  opacity: 1;
}

.section-content--collapsed {
  max-height: 0;
  opacity: 0;
  margin-bottom: 0;
}

/* Settings navigation - Compact category list */
.settings-nav-compact {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 20px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: none;
  border-radius: 8px;
}

.settings-nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  user-select: none;
}

.settings-nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
}

.settings-nav-item--active {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  font-weight: 500;
}

.settings-nav-item-icon {
  font-size: 10px;
  width: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: transform 0.2s ease;
}

.settings-nav-item--active .settings-nav-item-icon {
  opacity: 1;
}

.settings-nav-item-label {
  flex: 1;
}

.settings-category {
  scroll-margin-top: 20px;
}

/* Settings content styles */
.settings-content {
  padding: 4px 0;
}

.settings-section {
  margin-bottom: 20px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.settings-section-title {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.4;
}

.settings-text {
  margin: 0 0 6px 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

.settings-text:last-child {
  margin-bottom: 0;
}

.settings-meta {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  font-style: italic;
  margin-bottom: 12px;
}

.settings-list-items {
  margin: 8px 0;
  padding-left: 20px;
  list-style-type: disc;
  color: rgba(255, 255, 255, 0.7);
}

.settings-list-items li {
  margin-bottom: 6px;
  font-size: 13px;
  line-height: 1.5;
}

.settings-list-items li:last-child {
  margin-bottom: 0;
}

/* Layers category styling */
.layers-category {
  margin-bottom: 16px;
}

.layers-category:last-child {
  margin-bottom: 0;
}

.layers-category .title-collapsible {
  margin-bottom: 8px;
  align-items: baseline;
}

.layers-category .title {
  color: #b8bcc0;
  font-size: 13px;
  letter-spacing: 0.02em;
  font-weight: 500;
  line-height: 1.4;
}

.category-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
  max-height: 5000px; /* Large enough to accommodate all content */
  opacity: 1;
  transition:
    max-height 0.3s ease,
    opacity 0.2s ease,
    margin-bottom 0.3s ease;
  margin-bottom: 0;
}

.category-content--collapsed {
  max-height: 0;
  opacity: 0;
  margin-bottom: 0;
}

.sidebar .hint {
  color: #eaeaea;
  font-size: 13px;
  margin-bottom: 8px;
}

/* generic sidebar controls – exclude the toggle from this rule */
.sidebar button:not(.sidebar-toggle),
.sidebar select,
.sidebar input[type="range"] {
  width: 100%;
  margin-bottom: 8px;
  padding: 12px 12px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  color: #eaeaea;
  font-size: 14px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  text-align: left;
  cursor: pointer;
  outline: none;
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar button.active {
  background-color: rgba(255, 255, 255, 0.06);
}
.sidebar button .button-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.sidebar button .button-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.sidebar button:not(.sidebar-toggle):hover {
  background-color: rgba(255, 255, 255, 0.08);
}

/* header with square toggle */
.sidebar-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.sidebar-header-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.sidebar-header-hint {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 400;
  line-height: 1.5;
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  gap: 6px;
}

.sidebar-header-hint::before {
  content: "↗";
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  flex-shrink: 0;
}

.lumo-pro-thin {
  font-weight: 300;
}

/* Section Title Display (below header) */
.sidebar-section-title {
  padding: 16px 0 12px 0;
  margin-bottom: 16px;
}

.sidebar-section-title-text {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: -0.01em;
}

.sidebar-section-title-hint {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
  line-height: 1.4;
  letter-spacing: 0.01em;
}

/* square toggle: same size in expanded & collapsed sidebar */
.sidebar-toggle {
  flex: 0 0 auto;
  width: 30px;
  height: 30px; /* quadratic */
  box-sizing: border-box;
  padding: 0;
  position: relative;

  border-radius: 8px;
  display: grid;
  place-items: center;
  background: transparent;
  color: #e6e6e8;
  cursor: e-resize; /* Default: pointing right (will open/expand) */
  outline: none !important;
  box-shadow: none !important;
  border: none;
}
.sidebar-toggle--will-close {
  cursor: w-resize; /* Pointing left (will close/fold) */
}
.sidebar-toggle:hover {
  background: #2a2f34;
}

.sidebar-toggle:active {
  background: #1c1e21;
}

.sidebar-toggle:focus,
.sidebar-toggle:focus-visible {
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
}
.sidebar-toggle-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  object-fit: contain;
}
.sidebar-toggle-tooltip {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: #ffffff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0ms,
    visibility 0ms;
  z-index: 10000;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
}
.sidebar-toggle:hover .sidebar-toggle-tooltip {
  opacity: 1;
  visibility: visible;
  transition:
    opacity 0ms,
    visibility 0ms;
}

/* collapse behaviour */
.sidebar--collapsed {
  width: 64px;
  padding: 0;
  overflow: visible;
  border-radius: 16px;
  background: rgba(
    255,
    255,
    255,
    0.03
  ); /* More transparent for glassier feel */
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); /* Match app basket shadow */
  cursor: pointer;
  /* Inherit smooth transitions from .sidebar for width and padding */
  /* Additional transitions for background and box-shadow */
  transition:
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease,
    box-shadow 0.3s ease,
    backdrop-filter 0.3s ease;
}

.sidebar--collapsed:hover {
  background: rgba(
    255,
    255,
    255,
    0.06
  ); /* Slightly more opaque on hover, still very glassy */
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
}

.sidebar--collapsed .sidebar-divider {
  display: none;
}

.sidebar--collapsed .sidebar-icon-bar {
  width: 64px;
  border-radius: 16px;
  background: transparent;
  padding: 8px 0;
  justify-content: space-between; /* Space icons and profile */
}

.sidebar--collapsed .sidebar-scrollable {
  display: none; /* Keep display none for collapsed, opacity transition handles fade */
}

/* hide layer / legend content */
.sidebar-content {
  transition:
    opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.sidebar--collapsed .sidebar-content {
  opacity: 0;
  transform: translateX(-6px);
  pointer-events: none;
  height: 0;
}

/* when collapsed: hide title and hint but keep toggle */
.sidebar--collapsed .sidebar-header h2,
.sidebar--collapsed .sidebar-header-hint {
  display: none;
}

/* -------- ROUTE PLANNING -------- */
.route-planning-container {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.route-inputs-clean {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.route-clear-section {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.route-clear-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  padding: 0;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.route-clear-button:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: transparent;
  color: rgba(255, 255, 255, 0.9);
}

.route-clear-button:active {
  background: rgba(255, 255, 255, 0.08);
  transform: scale(0.95);
}

.route-clear-button svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  display: block;
}

.route-input-group {
  position: relative;
  width: 100%;
  min-height: 56px; /* Increased height for better spacing */
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.route-inputs-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}

.route-connector-line {
  position: absolute;
  left: 10px;
  top: 34px;
  height: 48px;
  width: 1px;
  background: rgba(255, 255, 255, 0.35);
  z-index: 0;
  pointer-events: none;
}

.route-input-graphics {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  padding-top: 14px;
  position: relative;
  z-index: 1;
}

.route-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.2s ease;
}

.route-icon svg {
  width: 100%;
  height: 100%;
  display: block;
}

.route-icon--start {
  color: rgba(255, 255, 255, 0.6);
}

.route-icon--end {
  color: rgba(255, 255, 255, 0.6);
}

.route-input-content {
  flex: 1;
  position: relative;
  min-width: 0;
}

.route-label-float {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
  pointer-events: none;
  transition: all 0.2s ease;
  z-index: 1;
  background: transparent;
}

.route-label-float--active {
  top: 10px;
  transform: translateY(0);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.route-select-wrapper {
  position: relative;
  width: 100%;
  display: block;
  overflow: visible;
}

.route-select {
  width: 100%;
  padding: 14px 36px 14px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #eaeaea;
  font-size: 14px;
  font-weight: 400;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image:
    linear-gradient(45deg, transparent 50%, rgba(255, 255, 255, 0.5) 50%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.5) 50%, transparent 50%);
  background-position:
    calc(100% - 12px) calc(50% - 1px),
    calc(100% - 6px) calc(50% + 1px);
  background-size:
    5px 5px,
    5px 5px;
  background-repeat: no-repeat;
  transition: all 0.2s ease;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  min-height: 48px;
  box-sizing: border-box;
  overflow: visible; /* Ensure text is not clipped */
  text-overflow: clip; /* Prevent ellipsis truncation */
}

.route-select-wrapper:has(.route-select-clear) .route-select {
  padding-right: 48px; /* Increased from 36px to accommodate clear button (16px button + 4px right + 28px space) */
  background-position:
    calc(100% - 24px) calc(50% - 1px),
    calc(100% - 18px) calc(50% + 1px);
}

.route-select-clear {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  max-width: 16px;
  max-height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.35);
  padding: 0;
  margin: 0;
  border-radius: 50%;
  transition: all 0.15s ease;
  z-index: 10;
  pointer-events: auto;
  box-sizing: border-box;
  overflow: hidden;
}

.route-select-clear:hover {
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.12);
}

.route-select-clear:active {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-50%) scale(0.9);
}

.route-select-clear svg {
  width: 8px;
  height: 8px;
  pointer-events: none;
  flex-shrink: 0;
}

.route-input-content:has(.route-label-float--active) .route-select,
.route-input-content:has(.route-select:focus) .route-select {
  padding-top: 22px;
  padding-bottom: 6px;
}

.route-input-content:has(.route-label-float--active)
  .route-select-wrapper:has(.route-select-clear)
  .route-select,
.route-input-content:has(.route-select:focus)
  .route-select-wrapper:has(.route-select-clear)
  .route-select {
  padding-right: 48px; /* Increased from 36px to accommodate clear button */
}

.route-input-content:has(.route-select:focus) .route-label-float {
  top: 10px;
  transform: translateY(0);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.route-select:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: transparent;
}

.route-select:focus {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

/* Make "Show more" option bold and italic with arrow */
.route-select option.option-show-more {
  font-weight: bold !important;
  font-style: italic !important;
}

/* Alternative approach for browsers that support it */
.route-select option[value="show_more"] {
  font-weight: bold !important;
  font-style: italic !important;
}

.route-swap-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.route-swap-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.05);
}

.route-swap-btn:active {
  transform: scale(0.95);
}

.route-swap-btn svg {
  flex-shrink: 0;
}

.route-plan-btn {
  width: 100%;
  padding: 12px 16px;
  background: #ffffff;
  color: #151517;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.route-plan-btn:hover:not(.route-plan-btn--disabled) {
  background: #f0f0f0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.route-plan-btn:active:not(.route-plan-btn--disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.route-plan-btn--disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
  opacity: 0.5;
}

.route-plan-btn--disabled:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  transform: none !important;
  box-shadow: none !important;
}

.route-plan-btn svg {
  flex-shrink: 0;
}

/* -------- ROUTE STATISTICS DISPLAY -------- */
.route-stats-container {
  margin-top: 24px;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.route-stats-header {
  margin-bottom: 4px;
}

.route-stats-header.title-collapsible {
  display: flex;
  align-items: baseline;
  gap: 6px;
  cursor: pointer;
  user-select: none;
  margin-bottom: 8px;
  padding: 0;
}

.route-stats-header.title-collapsible:hover {
  opacity: 0.8;
}

.route-stats-header.title-collapsible .title {
  color: #b8bcc0;
  font-size: 13px;
  letter-spacing: 0.02em;
  font-weight: 500;
  line-height: 1.4;
  margin: 0;
}

.route-stats-title {
  color: #b8bcc0;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.02em;
  margin: 0;
  text-transform: uppercase;
}

.route-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.route-stat-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.route-stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
  letter-spacing: -0.02em;
}

.route-stat-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.02em;
  text-transform: uppercase;
  margin-top: 4px;
}

/* -------- POI SECTION -------- */
.route-poi-section {
  margin-top: 20px;
  padding-top: 0;
  border-top: none;
}

.route-poi-header {
  margin-bottom: 12px;
}

.route-poi-title {
  color: #b8bcc0;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
  margin: 0;
  text-transform: uppercase;
}

.route-poi-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.route-poi-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.route-poi-count {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  min-width: 32px;
  text-align: center;
}

.route-poi-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.route-poi-type {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
}

.route-poi-frequency {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.route-poi-empty {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
  font-style: italic;
}

/* Enhanced POI display with mantras */
.route-summary-mantra {
  margin-top: 4px;
  margin-bottom: 20px;
  padding: 0;
}

.mantra-text {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #70f0c3;
  line-height: 1.5;
}

.route-info-section {
  margin: 16px 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.route-info-item {
  display: flex;
  gap: 8px;
  align-items: baseline;
}

.route-info-label {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  min-width: 70px;
}

.route-info-value {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
}

.route-poi-list-enhanced {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.route-poi-item-enhanced {
  display: flex;
  gap: 16px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
  transition: none;
  cursor: default;
}

.route-poi-item-enhanced:hover {
  background: transparent;
  border: none;
}

.route-poi-icon-wrapper {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: rgba(112, 240, 195, 0.15);
  border: none;
  border-radius: 12px;
}

.route-poi-count-large {
  font-size: 28px;
  font-weight: 700;
  color: #70f0c3;
  line-height: 1;
}

.route-poi-info-enhanced {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.route-poi-type-enhanced {
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 2px;
}

.route-poi-frequency-enhanced {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

.route-poi-mantra {
  margin-top: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  font-weight: 400;
}

.route-summary-footer {
  margin-top: 20px;
  padding: 12px 0;
  background: transparent;
  border: none;
  border-radius: 0;
}

.footer-text {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #70f0c3;
  line-height: 1.5;
  text-align: left;
}

.empty-mantra {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  line-height: 1.6;
  padding: 16px 0;
}

/* -------- ROUTE HISTORY -------- */
.route-history-wrapper {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.route-history-wrapper .route-history-header.title-collapsible {
  display: flex;
  align-items: baseline;
  gap: 6px;
  cursor: pointer;
  user-select: none;
  margin-bottom: 0;
  padding: 0;
}

.route-history-wrapper .route-history-header.title-collapsible:hover {
  opacity: 0.8;
}

.route-history-wrapper .route-history-header.title-collapsible .title {
  color: #b8bcc0;
  font-size: 13px;
  letter-spacing: 0.02em;
  font-weight: 500;
  line-height: 1.4;
  margin: 0;
}

.route-history-container {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.route-history-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  margin-bottom: 4px;
}

.route-history-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  margin-bottom: 4px;
  gap: 12px;
}

.route-history-clear-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 12px;
  margin-bottom: 0;
}

.route-history-clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #b8bcc0;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 48px;
  height: 48px;
  box-sizing: border-box;
}

.route-history-clear-btn:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: transparent;
  color: rgba(255, 255, 255, 0.9);
}

.route-history-clear-btn svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.route-history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  min-height: 200px;
}

.route-history-empty {
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
  text-align: center;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 200px;
}

.route-history-item {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 48px;
  box-sizing: border-box;
}

.route-history-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: transparent;
}

.route-history-route {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.route-history-from,
.route-history-to {
  color: #e9f7f2;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-history-arrow {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.5);
}

.route-history-date {
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
  white-space: nowrap;
  margin-left: 12px;
}

.route-swap-clean {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.route-swap-clean:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.route-swap-clean:active {
  background: rgba(255, 255, 255, 0.15);
}

/* -------- LEGEND BOX -------- */

/* -------- PROFILE SECTION -------- */
.profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 14px;
  margin-top: auto;
  border-top: 1px solid #1f2125;
  padding-bottom: 6px;
  position: relative; /* Ensure stable positioning */
}

/* Position profile in opened sidebar so JD avatar aligns with icon bar (same position as collapsed sidebar) */
.sidebar-main .profile {
  position: relative;
}

.sidebar-main .profile .avatar {
  position: absolute; /* Position relative to profile container */
  left: -67px; /* Position avatar left edge at 17px from sidebar left: sidebar-main starts at 64px, has 20px padding = 84px content start, avatar center at 32px means left edge at 17px, so 84px - 17px = 67px shift left */
  bottom: 6px; /* Match profile padding-bottom to align with collapsed sidebar (6px padding + 16px sidebar-main padding = 22px total, same as collapsed: 14px + 8px = 22px) */
  z-index: 11; /* Bring avatar above the icon bar (sidebar has z-index 10) */
  opacity: 1 !important; /* Always visible, no fade-in */
  visibility: visible !important; /* Always visible, no fade-in */
  transition:
    left 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    bottom 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Smooth transition matching sidebar */
}

/* When sidebar is collapsed, position avatar at exact same visual spot using same calculation */
.sidebar--collapsed .sidebar-icon-bar .profile {
  position: relative;
}

.sidebar--collapsed .sidebar-icon-bar .profile .avatar {
  position: absolute; /* Position relative to profile container */
  left: 17px; /* Avatar left edge at 17px from sidebar left (center at 32px, avatar is 30px wide, so 32px - 15px = 17px) */
  bottom: 14px; /* Match profile padding-bottom (14px padding + 8px icon-bar padding = 22px total from sidebar bottom) */
  z-index: 11;
  transition:
    left 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    bottom 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Smooth transition matching sidebar */
}

/* Allow sidebar-main to show overflow for profile section */
.sidebar-main {
  overflow: visible; /* Change from hidden to visible to show avatar */
}

.profile .avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #33343a, #1e1f23);
  color: #eaeaea;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    left 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Smooth transition when sidebar opens/closes */
}

.profile .info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.profile .name {
  font-size: 14px;
  font-weight: 500;
}

.profile .tier {
  font-size: 12px;
  color: #9aa0a6;
}

/* Profile in icon bar when collapsed */
.sidebar-icon-bar .profile {
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 8px 0 14px 0; /* Match bottom spacing with opened sidebar: 16px (sidebar-main bottom) + 6px (profile bottom) = 22px, icon-bar has 8px, so need 14px padding-bottom */
  margin-top: auto;
  border-top: none; /* Remove the line above profile */
  width: 100%;
  flex-shrink: 0;
  position: relative; /* Allow avatar to be positioned relative to this */
}

.sidebar-icon-bar .profile .info {
  display: none;
}

.sidebar-icon-bar .profile .avatar {
  width: 30px; /* Same size as in opened sidebar */
  height: 30px; /* Same size as in opened sidebar */
  font-size: 14px; /* Same size as in opened sidebar */
  position: relative; /* Maintain position for smooth transition */
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Smooth transition matching sidebar */
}

/* Hide profile in main content when collapsed */
.sidebar--collapsed .sidebar-main .profile {
  display: none;
}

/* Fixed avatar positioned outside sidebar-main to avoid fade-in - always visible */
.profile-avatar-fixed {
  position: absolute;
  left: 17px; /* Avatar left edge at 17px from sidebar left (center at 32px, avatar is 30px wide, so 32px - 15px = 17px) */
  bottom: 22px; /* Match collapsed sidebar: 14px padding + 8px icon-bar padding = 22px from sidebar bottom */
  z-index: 11; /* Bring avatar above the icon bar */
  pointer-events: none; /* Don't interfere with clicks */
  opacity: 1 !important; /* Always fully visible, no fade */
  visibility: visible !important; /* Always visible */
  /* No opacity or visibility transitions - avatar should never fade */
  transition: none !important;
}

/* When collapsed, avatar stays in same position (no change needed) */

.profile-avatar-fixed .avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #33343a, #1e1f23);
  color: #eaeaea;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* No transitions - should appear instantly */
  opacity: 1 !important;
  visibility: visible !important;
}

.profile-avatar-fixed--collapsed .avatar {
  opacity: 0.5 !important;
}

/* -------- POPUP -------- */
.popup {
  position: absolute;
  transform: translate(12px, -12px);
  background: #151517;
  border: 1px solid #2a2f34;
  padding: 10px 12px;
  border-radius: 12px;
  pointer-events: none;
  opacity: 0.95;
  z-index: 11;
}

.popup .row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

/* -------- LEGEND COMPONENT Z-INDEX -------- */
.legend {
  z-index: 9;
}

/* -------- TOP CONTROLS BAR (HIDDEN - MOVED TO APP BUTTONS) -------- */
.top-controls-bar {
  display: none; /* Hidden - all controls moved to app buttons */
}

.top-controls-bar:hover {
  background: #1a1b1e; /* Solid color on hover, match collapsed sidebar */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35); /* Stronger shadow on hover */
}

.top-controls-map-controls {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
  flex: 0 0 auto; /* Don't grow, don't shrink */
}

.top-controls-right {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  margin-left: auto;
  margin-right: 0;
}

.top-controls-bar .map-control-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  color: #e6e6e8;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease;
  padding: 0;
  box-sizing: border-box;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.top-controls-bar:not(:hover) .map-control-btn {
  background: transparent;
  box-shadow: none;
}

.top-controls-bar:hover .map-control-btn {
  background: rgba(26, 27, 30, 0.5);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.top-controls-bar:hover .map-control-btn:hover {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.top-controls-bar .map-control-btn:active {
  background: rgba(26, 27, 30, 0.7);
}

.top-controls-bar .map-control-btn.active {
  background: #1a1b1e;
  color: #ffffff;
}

.top-controls-bar .map-control-btn svg {
  display: block;
  margin: 0 auto;
  color: #ffffff;
  stroke: #ffffff;
  fill: none;
  width: 16px;
  height: 16px;
}

.top-controls-zurich-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: transparent;
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: none;
  padding: 0;
  margin: 0;
  flex-shrink: 0; /* Don't shrink */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition:
    opacity 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    transform 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    visibility 0ms 0.4s,
    background 0.3s ease,
    box-shadow 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.top-controls-zurich-btn--visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  pointer-events: auto;
}

.top-controls-bar:not(:hover) .top-controls-zurich-btn {
  background: transparent;
  box-shadow: none;
}

.top-controls-bar:hover .top-controls-zurich-btn {
  background: rgba(26, 27, 30, 0.5);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.top-controls-bar:hover .top-controls-zurich-btn:hover {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

/* -------- ZURICH APP BUTTON (TOP RIGHT CORNER) -------- */
/* -------- APP BASKET (GLASSMORPHIC CONTAINER) -------- */
.app-basket {
  position: fixed;
  top: 30px;
  right: 30px;
  z-index: 15;
  width: 224px; /* 12px padding + 46px + 8px gap + 46px + 8px gap + 92px (Zurich) + 12px padding = 224px */
  height: 116px; /* 12px padding + 42px + 8px gap + 42px + 12px padding = 116px */
  background: rgba(
    255,
    255,
    255,
    0.03
  ); /* More transparent for glassier feel */
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
  border: none;
  border-radius: 20px;
  padding: 12px; /* Reduced padding for better fit */
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
  gap: 12px; /* Gap between apps container and content when expanded */
  box-sizing: border-box;
  transition:
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    backdrop-filter 0.3s ease;
  overflow: hidden;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.app-basket--expanded {
  width: 336px; /* Match left sidebar width */
  height: calc(100vh - 60px); /* Extend from bottom to top with margins */
  top: 30px;
  bottom: 30px;
  padding: 16px; /* Increased padding when expanded */
}

.app-basket-apps-container {
  display: grid;
  grid-template-columns: 46px 46px 92px;
  grid-template-rows: 42px 42px;
  gap: 8px;
  flex-shrink: 0;
  align-items: start;
  justify-items: start;
  transition:
    grid-template-columns 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    grid-template-rows 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    gap 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
}

/* Animation: top-left of 2x2 grid */
.animation-app-container {
  grid-column: 1;
  grid-row: 1;
}

/* Chat: top-right of 2x2 grid */
.chat-app-button {
  grid-column: 2;
  grid-row: 1;
}

/* Legend: bottom-left of 2x2 grid */
.legend-app-button {
  grid-column: 1;
  grid-row: 2;
}

/* Phone: bottom-right of 2x2 grid */
.security-app-button {
  grid-column: 2;
  grid-row: 2;
}

/* Zurich: spans 2 rows on the right (bigger) */
.zurich-app-button {
  grid-column: 3;
  grid-row: 1 / 3;
}

.app-basket--expanded .app-basket-apps-container {
  grid-template-columns: repeat(5, 56px);
  grid-template-rows: 56px;
  gap: 8px;
  width: 100%;
  justify-content: center;
}

/* Reset grid positions when expanded - all apps in a single row */
.app-basket--expanded .zurich-app-button,
.app-basket--expanded .animation-app-container,
.app-basket--expanded .chat-app-button,
.app-basket--expanded .legend-app-button,
.app-basket--expanded .security-app-button {
  grid-column: auto;
  grid-row: 1;
}

/* App content inside basket */
.app-basket-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  position: relative;
  background: transparent;
  overflow: hidden;
}

.app-basket-content-label {
  position: absolute;
  top: 16px;
  left: 16px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.01em;
  z-index: 10;
}

.app-basket-content-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
  padding: 0;
  opacity: 0.7;
}

.app-basket-content-close:hover {
  opacity: 1;
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

.app-basket-content-close:active {
  transform: scale(0.95);
}

.app-basket-content-scrollable-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  margin-top: 48px; /* Space for header (label + close button) */
  scroll-padding-top: 48px; /* Additional scroll padding for better behavior */
}

.app-basket-content-scrollable {
  flex: 1;
  padding: 16px; /* Consistent padding matching basket frame */
  min-height: 0;
}

.app-basket-content-scrollable-wrapper::-webkit-scrollbar {
  width: 6px;
}

.app-basket-content-scrollable-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.app-basket-content-scrollable-wrapper::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.app-basket-content-scrollable-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.app-basket-app-section {
  width: 100%;
}

.app-basket-security-content,
.app-basket-animation-content {
  padding: 0; /* Remove padding since scrollable already has it */
  color: rgba(255, 255, 255, 0.9);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-content-title {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 12px 0;
  letter-spacing: -0.02em;
}

.security-introduction {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 24px 0;
  line-height: 1.6;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-category {
  margin-bottom: 24px;
}

.security-category-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  margin: 0 0 16px 0;
  letter-spacing: -0.01em;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-contacts-table {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
}

.security-contacts-header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  padding: 12px 0;
  border-bottom: none;
  font-weight: 600;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: -0.01em;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-contact-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  padding: 14px 0;
  border-bottom: none;
  transition: background-color 0.2s ease;
}

.security-contact-row:hover {
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  padding-left: 8px;
  padding-right: 8px;
  margin-left: -8px;
  margin-right: -8px;
}

.phone-contact-facility {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-contact-number {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  text-align: right;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-contact-facility {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-contact-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: color 0.2s ease;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-contact-link:hover {
  color: rgba(255, 255, 255, 1);
  text-decoration: underline;
}

.security-alert-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.security-alert-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.95);
}

.security-alert-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.security-alert-button.active {
  background: rgba(255, 68, 68, 0.15);
  color: #ff4444;
}

.security-alert-button.active:hover {
  background: rgba(255, 68, 68, 0.2);
}

.security-alert-button svg {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

.security-alert-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 12px 0 0 0;
  line-height: 1.5;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.lumo-score-display {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 12px;
  border: none;
}

.lumo-score-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.lumo-score-values {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.lumo-score-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.lumo-score-route-type {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.lumo-score-number {
  font-size: 20px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.02em;
}

.uber-link-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
}

.uber-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  margin-bottom: 4px;
}

.uber-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.uber-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.6;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.uber-import-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  width: 100%;
  justify-content: center;
}

.uber-import-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.95);
}

.uber-import-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.uber-import-button svg {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

.map-controls-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
}

.map-control-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 18px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  color: rgba(255, 255, 255, 0.9);
  min-height: 90px;
  position: relative;
  overflow: hidden;
}

.map-control-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0) 100%
  );
  opacity: 0;
  transition: opacity 0.25s ease;
}

.map-control-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.map-control-card:hover::before {
  opacity: 1;
}

.map-control-card:active {
  transform: translateY(0);
}

.map-control-card.active {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.map-control-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  transition: all 0.25s ease;
  position: relative;
  z-index: 1;
}

.map-control-card:hover .map-control-icon {
  background: rgba(255, 255, 255, 0.12);
}

.map-control-card.active .map-control-icon {
  background: rgba(255, 255, 255, 0.16);
}

.map-control-icon svg {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.9);
  stroke: rgba(255, 255, 255, 0.9);
  fill: none;
  transition: all 0.25s ease;
}

.map-control-card:hover .map-control-icon svg {
  color: rgba(255, 255, 255, 1);
  stroke: rgba(255, 255, 255, 1);
}

.map-control-label {
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.2px;
  color: rgba(255, 255, 255, 0.75);
  transition: color 0.25s ease;
  position: relative;
  z-index: 1;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.map-control-card:hover .map-control-label {
  color: rgba(255, 255, 255, 0.9);
}

.map-control-card.active .map-control-label {
  color: rgba(255, 255, 255, 1);
  font-weight: 600;
}

/* Basket expand transition */
.basket-expand-enter-active {
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.basket-expand-leave-active {
  transition: all 0.35s cubic-bezier(0.55, 0.06, 0.68, 0.19);
}

.basket-expand-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.basket-expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.zurich-app-button {
  position: relative;
  width: 92px; /* Larger app button in collapsed state */
  height: 92px; /* Make it quadratic (width = height) */
  background: rgba(26, 27, 30, 0.3);
  border: none;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease,
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
  box-sizing: border-box;
  flex-shrink: 0;
}

.app-basket--expanded .zurich-app-button {
  width: 56px;
  height: 56px;
  border-radius: 12px;
}

.zurich-app-button:hover {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.zurich-app-button-inner {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease;
  box-sizing: border-box;
}

.app-basket--expanded .zurich-app-button-inner {
  width: 100%;
  height: 100%;
}

.zurich-app-button-inner:hover {
  transform: scale(1.05);
}

.zurich-app-button-inner:active {
  transform: scale(0.95);
}

.zurich-app-icon {
  width: 24px;
  height: 24px;
  display: block;
  flex-shrink: 0;
  opacity: 0.4;
  transition:
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    opacity 0.3s ease;
}

.zurich-app-button:hover .zurich-app-icon {
  opacity: 1;
}

.app-basket--expanded .zurich-app-icon {
  width: 20px;
  height: 20px;
}

.zurich-app-location {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  transition:
    gap 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    padding 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
}

.app-basket--expanded .zurich-app-location {
  gap: 3px;
  padding: 6px;
}

.zurich-app-location-name {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.2;
  white-space: nowrap;
  text-align: center;
  opacity: 0.4;
  transition:
    font-size 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    opacity 0.3s ease;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.zurich-app-button:hover .zurich-app-location-name {
  opacity: 1;
}

.app-basket--expanded .zurich-app-location-name {
  font-size: 11px;
}

.zurich-app-location-time {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #b0b0b0;
  line-height: 1.2;
  white-space: nowrap;
  opacity: 0.4;
  transition:
    font-size 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    opacity 0.3s ease;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.zurich-app-button:hover .zurich-app-location-time {
  opacity: 1;
}

.app-basket--expanded .zurich-app-location-time {
  font-size: 10px;
}

.zurich-app-time-text {
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

/* Map Controls Overlay */
.map-controls-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 14;
  background: transparent;
}

/* -------- ANIMATION APP BUTTON -------- */
.animation-app-container {
  position: relative;
  width: 46px;
  height: 42px;
  min-width: 0;
  min-height: 0;
  transition:
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
}

.app-basket--expanded .animation-app-container {
  width: 56px;
  height: 56px;
}

.animation-app-button {
  width: 100%;
  height: 100%;
  background: rgba(26, 27, 30, 0.3);
  border: none;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease,
    transform 0.2s ease,
    border-radius 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
  box-sizing: border-box;
}

.app-basket--expanded .animation-app-button {
  border-radius: 10px;
}

.animation-app-button:hover {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  transform: scale(1.05);
}

.animation-app-button:active {
  transform: scale(0.95);
}

.animation-app-button--expanded {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.animation-app-button svg {
  width: 20px;
  height: 20px;
  color: #ffffff;
  stroke: #ffffff;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.4;
  transition:
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    opacity 0.3s ease;
}

.animation-app-button:hover svg {
  opacity: 1;
}

.animation-app-button--expanded svg {
  opacity: 1 !important;
  color: #ffffff !important;
  stroke: #ffffff !important;
}

.app-basket--expanded .animation-app-button svg {
  width: 16px;
  height: 16px;
}

/* Animation Content Styles */
.animation-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 24px;
  width: 100%;
  justify-content: center;
}

.animation-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.animation-button:active:not(:disabled) {
  transform: scale(0.98);
}

.animation-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.animation-button svg {
  flex-shrink: 0;
}

.animation-reset-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
}

.animation-reset-button:hover {
  color: rgba(255, 255, 255, 0.9);
}

.animation-reset-button svg {
  flex-shrink: 0;
}

.animation-coloring-mode {
  margin-top: 24px;
  padding-top: 0;
  border-top: none;
}

.animation-coloring-label {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.animation-coloring-options {
  display: flex;
  gap: 8px;
  flex-direction: column;
}

.animation-coloring-button {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  text-align: left;
}

.animation-coloring-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
}

.animation-coloring-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.animation-coloring-button.active {
  background: rgba(100, 180, 255, 0.15);
  color: #ffffff;
}

.animation-coloring-button.active:hover {
  background: rgba(100, 180, 255, 0.2);
}

.animation-coloring-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.animation-coloring-button.active .animation-coloring-hint {
  color: rgba(255, 255, 255, 0.7);
}

.animation-content {
  padding: 0;
}

.animation-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.5;
  margin: 0;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

/* -------- CHAT APP BUTTON -------- */
.chat-app-button {
  position: relative;
  width: 46px;
  height: 42px;
  background: rgba(26, 27, 30, 0.3);
  border: none;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease,
    transform 0.2s ease,
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
  box-sizing: border-box;
}

.app-basket--expanded .chat-app-button {
  width: 56px;
  height: 56px; /* Square to match other apps */
}

.chat-app-button:hover {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  transform: scale(1.05);
}

.chat-app-button:active {
  transform: scale(0.95);
}

.chat-app-button--active {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.chat-app-button svg {
  width: 20px;
  height: 20px;
  color: #ffffff;
  stroke: #ffffff;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.4;
  transition:
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    opacity 0.3s ease;
}

.chat-app-button:hover svg {
  opacity: 1;
}

.chat-app-button--active svg {
  opacity: 1 !important;
  color: #ffffff !important;
  stroke: #ffffff !important;
}

.app-basket--expanded .chat-app-button svg {
  width: 16px;
  height: 16px;
}

/* -------- LEGEND APP BUTTON -------- */
.legend-app-button {
  position: relative;
  width: 46px;
  height: 42px;
  background: rgba(26, 27, 30, 0.3);
  border: none;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease,
    transform 0.2s ease,
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
  box-sizing: border-box;
}

.app-basket--expanded .legend-app-button {
  width: 56px;
  height: 56px;
}

.legend-app-button:hover {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  transform: scale(1.05);
}

.legend-app-button:active {
  transform: scale(0.95);
}

.legend-app-button--active {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.legend-app-button svg {
  width: 20px;
  height: 20px;
  color: #ffffff;
  stroke: #ffffff;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.4;
  transition:
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    opacity 0.3s ease;
}

.legend-app-button:hover svg {
  opacity: 1;
}

.legend-app-button--active svg {
  opacity: 1 !important;
  color: #ffffff !important;
  stroke: #ffffff !important;
}

.app-basket--expanded .legend-app-button svg {
  width: 16px;
  height: 16px;
}

/* -------- SECURITY APP BUTTON -------- */
.security-app-button {
  position: relative;
  width: 46px;
  height: 42px;
  background: rgba(26, 27, 30, 0.3);
  border: none;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    background 0.3s ease,
    box-shadow 0.3s ease,
    transform 0.2s ease,
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
  box-sizing: border-box;
}

.app-basket--expanded .security-app-button {
  width: 56px;
  height: 56px;
}

.security-app-button:hover {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  transform: scale(1.05);
}

.security-app-button:active {
  transform: scale(0.95);
}

.security-app-button--active {
  background: #1a1b1e;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.security-app-button svg {
  width: 20px;
  height: 20px;
  color: #ffffff;
  stroke: #ffffff;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  opacity: 0.4;
  transition:
    width 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    height 0.3s cubic-bezier(0.16, 0.84, 0.24, 1),
    opacity 0.3s ease;
}

.security-app-button:hover svg {
  opacity: 1;
}

.security-app-button--active svg {
  opacity: 1 !important;
  color: #ffffff !important;
  stroke: #ffffff !important;
}

.app-basket--expanded .security-app-button svg {
  width: 16px;
  height: 16px;
}

.top-controls-zurich-btn:active {
  background: rgba(26, 27, 30, 0.7);
}

.top-controls-zurich-icon {
  width: 20px;
  height: 20px;
  display: block;
  flex-shrink: 0;
}

.top-controls-location {
  display: none; /* Hidden by default, doesn't take space */
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  margin-right: 0; /* No margin, gap handled by parent */
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition:
    opacity 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    transform 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    visibility 0ms 0.4s;
  pointer-events: none;
  flex-shrink: 1; /* Allow shrinking */
  min-width: 0; /* Allow text truncation */
  overflow: hidden; /* Prevent overflow */
}

.top-controls-location--visible {
  display: flex; /* Show when visible */
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  pointer-events: auto;
}

.top-controls-location .location-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.top-controls-location .location-time {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #b0b0b0;
  line-height: 1.2;
  white-space: nowrap;
}

.top-controls-location .time-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  color: #b0b0b0;
}

.top-controls-location .time-text {
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
}

.top-controls-location .time-colon {
  animation: blink 1s infinite;
}

/* -------- MAP SCALE -------- */
.map-controls-over-scale {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 12;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
  transition: right 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
}

.map-controls-over-scale--basket-expanded {
  right: 386px; /* 336px (basket width) + 30px (original right) + 20px (padding) */
}

.map-control-btn-over-scale {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(26, 27, 30, 0.15);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0;
}

.map-control-btn-over-scale:hover {
  background: rgba(26, 27, 30, 0.6);
  color: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.map-control-btn-over-scale:active {
  transform: translateY(0);
}

.map-scale {
  position: fixed;
  bottom: 30px;
  left: 396px; /* Positioned with 30px gap from open sidebar (30px + 336px sidebar + 30px gap) */
  z-index: 12;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  pointer-events: none;
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 0.4s ease,
    transform 0.4s ease,
    left 0.3s cubic-bezier(0.16, 0.84, 0.24, 1);
}

.map-scale--visible {
  opacity: 0.5;
  transform: translateY(0);
}

.map-scale--sidebar-collapsed {
  left: 124px; /* Positioned with 30px gap from collapsed sidebar (30px + 64px sidebar + 30px gap) */
}

.scale-line {
  width: 80px;
  height: 7px;
  background: rgba(255, 255, 255, 0.4);
  border-top: 1px solid rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
}

.scale-label {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.5);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 400;
  letter-spacing: 0.01em;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* -------- MAP CITY BUTTON -------- */
/* Old map city button - hidden (moved to top controls bar) */
.map-city-button {
  display: none;
}

.map-city-button svg {
  opacity: 1;
}
.map-city-button--visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  transition:
    opacity 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    transform 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    visibility 0ms;
  pointer-events: auto;
}
.map-city-button--visible:hover {
  background: #151517;
}
.map-city-button--visible:active {
  background: #1c1e21;
}
.map-city-button-icon {
  width: 28px;
  height: 28px;
  display: block;
  flex-shrink: 0;
}

/* -------- MAP LOCATION -------- */
/* Old map location - hidden (moved to top controls bar) */
.map-location {
  display: none;
}

.location-name {
  font-size: 26px;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 600;
  letter-spacing: -0.01em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
}

.location-time {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
  letter-spacing: 0.01em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  gap: 0;
}

.time-icon {
  color: rgba(255, 255, 255, 0.85);
  flex-shrink: 0;
  margin-right: 8px;
}

.time-text {
  display: inline;
}

.time-colon {
  animation: fadeInOut 1s ease-in-out infinite;
  display: inline-block;
}

@keyframes fadeInOut {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.2;
  }
}

/* -------- LEGEND BOX -------- */
.sidebar-legend {
  margin-top: 0;
}

/* -------- ROUTE DETAILS POPUP -------- */
/* Route Details Popup Slide Transition */
.route-details-slide-enter-active .route-details-popup {
  transition: all 0.2s cubic-bezier(0.16, 0.84, 0.24, 1);
}

.route-details-slide-leave-active .route-details-popup {
  transition: all 0.2s cubic-bezier(0.16, 0.84, 0.24, 1);
}

.route-details-slide-enter-from .route-details-popup {
  opacity: 0;
  transform: translateX(100%);
}

.route-details-slide-leave-to .route-details-popup {
  opacity: 0;
  transform: translateX(100%);
}

.route-details-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  pointer-events: none;
}

.route-details-popup {
  position: fixed;
  top: 106px; /* Aligned below top controls bar (30px top + 64px height + 12px gap) */
  right: 30px; /* Match the right position of the time display */
  bottom: 400px; /* Reduced height - shorter popup */
  width: 280px; /* Slimmer width */
  max-width: calc(100vw - 40px);
  max-height: none; /* Use bottom positioning instead */
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  border: none;
  border-radius: 16px; /* Match sidebar border-radius */
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  pointer-events: auto;
}

.legend-popup {
  bottom: 200px; /* More space for legend content */
}

.legend-popup-content {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(100vh - 350px);
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.route-details-popup-label {
  position: absolute;
  top: 12px;
  left: 20px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.01em;
  z-index: 10;
}

.route-details-popup-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
  padding: 0;
  opacity: 0.7;
}

.route-details-popup-close:hover {
  opacity: 1;
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

.route-details-popup-close:active {
  transform: scale(0.95);
}

.route-details-popup-close svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
}

.route-details-popup-header {
  padding: 32px 32px 0 32px;
  flex-shrink: 0;
  border-bottom: none;
  z-index: 1;
}

.route-details-popup-content {
  padding: 40px 32px 80px 32px; /* Extra top padding to shift content down, extra bottom padding for fixed input */
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.route-details-popup-content::-webkit-scrollbar {
  width: 8px;
}

.route-details-popup-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.route-details-popup-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.route-details-popup-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.route-details-popup-title {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 24px 0;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.5px;
}

.route-details-popup-info {
  margin-bottom: 16px;
  padding-bottom: 0;
  border-bottom: none;
}

.route-details-intro {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start; /* Align content to left for speech bubble */
  margin-bottom: 4px;
}

@keyframes chatBubbleAppear {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.route-details-intro-greeting {
  font-size: 16px;
  line-height: 1.4;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 400;
  letter-spacing: -0.02em;
  margin: 0;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 18px 0;
  position: relative;
  display: inline-block;
  max-width: calc(100% - 20px);
  align-self: flex-start;
  margin: 0;
  word-wrap: break-word;
  box-shadow: none;
  animation: chatBubbleAppear 0.5s ease-out 0.4s forwards;
  opacity: 0;
}

/* Disable animations when route has been shown before */
.route-already-shown .route-details-intro-greeting {
  animation: none !important;
  opacity: 1 !important;
}

.route-details-greeting-bold {
  font-weight: 800;
}

.route-details-intro-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 18px 0;
  position: relative;
  display: inline-block;
  max-width: calc(100% - 20px);
  align-self: flex-start;
  word-wrap: break-word;
  box-shadow: none;
  font-weight: 400;
  letter-spacing: 0.01em;
  animation: chatBubbleAppear 0.5s ease-out 0.7s forwards;
  opacity: 0;
}

.route-already-shown .route-details-intro-text {
  animation: none !important;
  opacity: 1 !important;
}

.route-details-tip {
  margin: 0;
  font-size: 12px;
  line-height: 1.4;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 18px 0;
  position: relative;
  display: inline-block;
  max-width: calc(100% - 20px);
  align-self: flex-start;
  word-wrap: break-word;
  box-shadow: none;
  font-weight: 400;
  letter-spacing: 0.01em;
  opacity: 0.9;
}

.route-details-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: none;
  transition: all 0.2s ease;
}

.route-details-info-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.route-details-info-item:last-child {
  margin-bottom: 0;
}

.route-details-info-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.route-details-info-value {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.route-details-document {
  margin: 0;
  max-width: calc(100% - 20px);
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 18px 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  margin-top: 10px;
  animation: chatBubbleAppear 0.5s ease-out 1s forwards;
  opacity: 0;
}

.route-already-shown .route-details-document {
  animation: none !important;
  opacity: 1 !important;
}

.route-details-document-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background 0.2s ease;
}

.route-details-document-header:hover {
  background: rgba(255, 255, 255, 0.08);
}

.route-details-document-icon {
  width: 14px;
  height: 14px;
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.route-details-document-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: 0.01em;
}

.route-details-document-content {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.route-details-document-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.route-details-document-item-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.route-details-document-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.route-details-poi-section {
  margin-top: 8px;
}

.route-details-mantra {
  margin-bottom: 20px;
}

.route-details-mantra-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin: 0;
  line-height: 1.5;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.route-details-poi-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.route-details-poi-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 16px;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.route-details-poi-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.route-details-poi-icon-wrapper {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: none;
}

.route-details-poi-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #70f0c3;
}

.route-details-document-item-icon .route-details-poi-icon {
  width: 18px;
  height: 18px;
}

.route-details-poi-icon svg {
  width: 100%;
  height: 100%;
  stroke: currentColor;
  fill: none;
}

.route-details-poi-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.route-details-poi-type {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.route-details-poi-frequency {
  font-size: 14px;
  color: #ffffff;
  font-weight: 600;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.route-details-poi-frequency-bright {
  color: #64b4ff;
  margin-bottom: 3px;
  line-height: 1.3;
}

.route-details-poi-mantra {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.4;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.route-details-footer {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

/* Quick animation for empty state messages */
@keyframes quickFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.route-details-footer-bubble--quick {
  animation: quickFadeIn 0.5s ease forwards !important;
  opacity: 0;
}

/* Welcome bubbles - same animation as route-generated bubbles */
.route-details-footer-bubble--welcome {
  animation: chatBubbleAppear 0.5s ease-out forwards;
  opacity: 0;
}

.route-details-footer-bubble--welcome.route-details-footer-bubble--greeting {
  animation: chatBubbleAppear 0.5s ease-out 0.3s forwards;
}

.route-details-footer-bubble--welcome:nth-of-type(2) {
  animation: chatBubbleAppear 0.5s ease-out 0.6s forwards;
}

.route-details-footer-bubble--welcome:nth-of-type(3) {
  animation: chatBubbleAppear 0.5s ease-out 0.9s forwards;
}

.route-details-document.route-details-footer-bubble--welcome {
  animation: chatBubbleAppear 0.5s ease-out 1.2s forwards;
}

.route-details-footer-bubble {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 18px 0;
  position: relative;
  display: inline-block;
  max-width: calc(100% - 20px);
  align-self: flex-start;
  word-wrap: break-word;
  box-shadow: none;
  font-weight: 400;
  letter-spacing: 0.01em;
  animation: chatBubbleAppear 0.5s ease-out 1.3s forwards;
  opacity: 0;
}

.route-details-footer-button {
  display: inline;
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  color: #ffffff;
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
  cursor: pointer;
  font-size: inherit;
  font-family: inherit;
  line-height: inherit;
  transition: opacity 0.2s ease;
}

.route-details-footer-button:hover {
  opacity: 0.7;
}

.route-details-footer-button:active {
  opacity: 0.5;
}

/* Greeting bubble - bigger font to match route greeting */
.route-details-footer-bubble--greeting {
  font-size: 16px !important;
  font-weight: 800;
  letter-spacing: -0.02em;
}

/* Document chevron */
.route-details-document-chevron {
  margin-left: auto;
  transition: transform 0.2s ease;
  opacity: 0.6;
}

.route-details-document-chevron--expanded {
  transform: rotate(180deg);
}

/* Document text content */
.route-details-document-text {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.85);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: 0.01em;
  padding: 0 16px 16px 16px;
}

/* Document expand transition */
.document-expand-enter-active,
.document-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.document-expand-enter-from {
  opacity: 0;
  max-height: 0;
}

.document-expand-enter-to {
  opacity: 1;
  max-height: 200px;
}

.document-expand-leave-from {
  opacity: 1;
  max-height: 200px;
}

.document-expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.route-already-shown .route-details-footer-bubble {
  animation: none !important;
  opacity: 1 !important;
}

.route-details-response-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  margin-top: 10px;
}

.route-details-response-bubble {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 18px 0;
  position: relative;
  display: inline-block;
  max-width: calc(100% - 20px);
  align-self: flex-start;
  word-wrap: break-word;
  box-shadow: none;
  font-weight: 400;
  letter-spacing: 0.01em;
  animation: chatBubbleAppear 0.5s ease-out 0.6s forwards;
  opacity: 0;
}

/* Disable animations when response was already shown for this route */
.response-already-shown .route-details-response-bubble {
  animation: none !important;
  opacity: 1 !important;
}

.route-details-safety-bubble {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 18px 0;
  position: relative;
  display: inline-block;
  max-width: calc(100% - 20px);
  align-self: flex-start;
  word-wrap: break-word;
  box-shadow: none;
  font-weight: 400;
  letter-spacing: 0.01em;
  animation: chatBubbleAppear 0.5s ease-out 1.2s forwards;
  opacity: 0;
}

/* Disable animations when response was already shown for this route */
.response-already-shown .route-details-safety-bubble {
  animation: none !important;
  opacity: 1 !important;
}

.route-details-input-container {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  z-index: 10;
  display: flex;
  justify-content: flex-end;
}

.route-details-input-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(128, 128, 128, 0.2);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(128, 128, 128, 0.3);
  color: rgba(160, 160, 160, 0.9);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  padding: 0;
}

.route-details-input-button:hover {
  background: rgba(128, 128, 128, 0.3);
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.route-details-input-button:active {
  transform: scale(0.95);
}

.route-details-input {
  width: 100%;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  color: #ffffff;
  font-size: 14px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.route-details-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.route-details-input:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.25);
}

.route-details-user-message {
  margin: 0 0 0 auto;
  font-size: 14px;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.9);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  padding: 12px 16px;
  background: rgba(112, 240, 195, 0.15);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 18px 18px 0 18px; /* Sharp edge on right */
  position: relative;
  display: inline-block;
  max-width: calc(100% - 20px);
  align-self: flex-end;
  word-wrap: break-word;
  box-shadow: none;
  font-weight: 400;
  letter-spacing: 0.01em;
  margin-top: 10px;
  animation: chatBubbleAppear 0.5s ease-out forwards;
  opacity: 0;
}

.route-already-shown .route-details-user-message {
  animation: none !important;
  opacity: 1 !important;
}

.route-details-empty {
  text-align: center;
  padding: 40px 20px;
}

.route-details-empty-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  margin: 0;
  line-height: 1.6;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

/* Fade transition for route content updates */
.fade-content-enter-active,
.fade-content-leave-active {
  transition:
    opacity 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.fade-content-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.fade-content-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Basket Reload Animation - smooth transition when content changes */
.basket-reload-enter-active {
  transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.basket-reload-leave-active {
  transition: all 0.2s cubic-bezier(0.55, 0.06, 0.68, 0.19);
}

.basket-reload-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
}

.basket-reload-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

/* Label fade animation */
.label-fade-enter-active {
  transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.label-fade-leave-active {
  transition: all 0.15s cubic-bezier(0.55, 0.06, 0.68, 0.19);
}

.label-fade-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}

.label-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>

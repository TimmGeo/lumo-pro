<template>
  <div class="app">
    <!-- Main map viewer -->
    <MapboxViewer
      :lightingVisible="lightingVisible"
      :vibrancyVisible="vibrancyVisible"
      :combinedVisible="combinedVisible"
      :heightScale="heightScale"
      :showHubs="routingHubsVisible"
      @ready="onViewerReady"
      :focusZurichKey="zurichFocusKey"
      @zurichZoomComplete="handleZurichZoomComplete"
      @zoom="handleMapZoom"
      @move="handleMapMove"
      @mapReady="handleMapReady"
    />

    <!-- Sidebar controls -->
    <aside
      :class="['sidebar', { 'sidebar--collapsed': sidebarCollapsed }]"
      :style="!sidebarCollapsed ? { width: sidebarWidth + 'px' } : {}"
      @mouseenter="handleSidebarMouseEnter"
      @mouseleave="handleMouseLeave"
      @click="handleSidebarClick"
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
            <img
              src="/Lumo_icon_grey.svg"
              alt="Lumo"
              class="sidebar-logo-icon"
            />
          </div>

          <button
            class="sidebar-icon-btn"
            :class="{ active: activeSidebarTab === 'routing' }"
            @click.stop="activeSidebarTab = 'routing'"
            aria-label="Routing"
          >
            <img src="/routing_hubs.svg" alt="Routing" />
            <span class="sidebar-icon-tooltip">Routing</span>
          </button>
          <button
            class="sidebar-icon-btn"
            :class="{ active: activeSidebarTab === 'layers' }"
            @click.stop="activeSidebarTab = 'layers'"
            aria-label="Layers"
          >
            <img src="/lighting.svg" alt="Layers" />
            <span class="sidebar-icon-tooltip">Layers</span>
          </button>
          <button
            class="sidebar-icon-btn"
            :class="{ active: activeSidebarTab === 'statistics' }"
            @click.stop="activeSidebarTab = 'statistics'"
            aria-label="Statistics"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18M9 21V9" />
            </svg>
            <span class="sidebar-icon-tooltip">Statistics</span>
          </button>
        </div>

        <!-- Settings icon above profile -->
        <div class="sidebar-icon-bar-bottom">
          <button
            class="sidebar-icon-btn sidebar-icon-btn--settings"
            :class="{ active: activeSidebarTab === 'settings' }"
            @click.stop="activeSidebarTab = 'settings'"
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
                d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
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
            <h2 class="nowrap">{{ sectionTitle }}</h2>
            <p class="sidebar-header-hint">{{ sectionHint }}</p>
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
                        <select v-model="startHub" class="route-select">
                          <option disabled value=""></option>
                          <option v-for="h in hubs" :key="h.id" :value="h.id">
                            {{ h.name }}
                          </option>
                        </select>
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
                        <select v-model="endHub" class="route-select">
                          <option disabled value=""></option>
                          <option v-for="h in hubs" :key="h.id" :value="h.id">
                            {{ h.name }}
                          </option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  class="route-plan-btn"
                  :class="{ 'route-plan-btn--disabled': !canPlanRoute }"
                  :disabled="!canPlanRoute"
                  @click="route"
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
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                  Plan Route
                </button>
              </div>
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
                    Lighting
                  </button>
                  <button
                    :class="{ active: vibrancyVisible }"
                    @click="selectLayer('vibrancy')"
                  >
                    Vibrancy
                  </button>
                  <button
                    :class="{ active: combinedVisible }"
                    @click="selectLayer('combined')"
                  >
                    Combined
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

          <!-- Statistics (formerly Color Legend) -->
          <div
            v-show="activeSidebarTab === 'statistics'"
            class="group sidebar-legend sidebar-content"
          >
            <div class="section-content">
              <div
                class="legend-box-new"
                :class="{
                  'legend-box-new--highlight': legendOverBox,
                }"
                ref="legendBoxRef"
              >
                <Legend
                  v-if="!legendDraggedOut"
                  :mode="mode"
                  :in-box="true"
                  :dragged-out="false"
                  :position="legendPosition"
                  @take-out="handleLegendDragOut"
                  @drag-back="handleLegendDragBack"
                  @drag-start="() => {}"
                  @drag-end="() => {}"
                  @position-update="handleLegendPositionUpdate"
                />
                <div v-else class="legend-box-empty">
                  <svg
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      d="M12 2L2 7L12 12L22 7L12 2Z"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M2 17L12 22L22 17"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M2 12L12 17L22 12"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <span class="legend-box-empty-text">Legend is outside</span>
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

    <!-- Scale indicator -->
    <div class="map-scale" :class="{ 'map-scale--visible': mapZoom >= 11 }">
      <div class="scale-line"></div>
      <div class="scale-label">{{ scaleText }}</div>
    </div>

    <!-- City button (shows when not at Zurich level) -->
    <button
      class="map-city-button"
      :class="{ 'map-city-button--visible': mapZoom < 11 }"
      @click="focusZurich"
      aria-label="Zoom to Zurich"
    >
      <svg
        class="map-city-button-icon"
        width="20"
        height="20"
        viewBox="0 0 32.42 39.57"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M16.21,0C7.27,0,0,7.27,0,16.21c0,2.57.59,5.04,1.73,7.29,3.17,7.01,9.89,13.08,12.62,15.35.39.35,1.09.72,1.89.72.65,0,1.26-.24,1.79-.7,2.75-2.28,9.48-8.35,12.63-15.33,1.16-2.29,1.75-4.76,1.75-7.33C32.42,7.27,25.15,0,16.21,0ZM30.66,16.21c0,2.29-.53,4.5-1.57,6.55v.02c-3.02,6.68-9.53,12.53-12.19,14.75-.64.56-1.23.14-1.4-.01-2.65-2.2-9.15-8.06-12.18-14.77-1.04-2.04-1.56-4.24-1.56-6.53C1.76,8.24,8.24,1.76,16.21,1.76s14.45,6.48,14.45,14.45Z"
          fill="#ffffff"
        />
      </svg>
    </button>

    <!-- Location indicator -->
    <div
      class="map-location"
      :class="{ 'map-location--visible': mapZoom >= 11 && locationText }"
    >
      <div class="location-name">{{ locationText }}</div>
      <div class="location-time">
        <!-- Sun icon for daylight hours (6 AM - 8 PM) -->
        <svg
          v-if="isDaylight"
          class="time-icon"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
        <!-- Moon icon for nighttime hours -->
        <svg
          v-else
          class="time-icon"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
        <span class="time-text" v-if="zurichTime">
          {{ zurichTime.split(":")[0] }}<span class="time-colon">:</span
          >{{ zurichTime.split(":")[1] }}
        </span>
      </div>
    </div>

    <!-- Dragged out legend (floating) -->
    <Legend
      v-if="legendDraggedOut"
      :mode="mode"
      :dragged-out="true"
      :in-box="false"
      :position="legendPosition"
      :size="legendSize"
      @close="handleLegendClose"
      @position-update="handleLegendPositionUpdate"
      @size-update="handleLegendSizeUpdate"
      @drag-back="handleLegendDragBack"
      class="legend-floating"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import MapboxViewer from "./components/MapboxViewer.vue";
import Legend from "./components/Legend.vue";
import Walkthrough from "./components/Walkthrough.vue";
import GuidedTour from "./components/GuidedTour.vue";

// UI state
const heightScale = ref(1.5);
// Layer visibility states - only one can be active at a time
const lightingVisible = ref(true);
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
const startHub = ref("");
const endHub = ref("");
const hubs = ref([
  { id: "HB", name: "Zürich HB" },
  { id: "BEL", name: "Bellevue" },
  { id: "LS", name: "Langstrasse" },
  { id: "EW", name: "Escher-Wyss" },
]);

// Hover popup data
const popup = ref({ show: false, x: 0, y: 0, lights: 0, pois: 0, hub: "—" });

let api = null;

// sidebar collapse state
const sidebarCollapsed = ref(false);
const sidebarWidth = ref(320);
const isResizing = ref(false);
const isHovering = ref(false);
const showWalkthrough = ref(true);
const routingHubsVisible = ref(true);
const showGuidedTour = ref(false);
const zurichFocusKey = ref(0);
const pendingTourAfterZoom = ref(false);
const mapReady = ref(false);

// Hover timer for opening collapsed sidebar
let hoverTimer = null;
const HOVER_DELAY = 800; // 800ms delay before opening
// Hover timer for closing expanded sidebar
let sidebarCloseTimer = null;
const SIDEBAR_CLOSE_DELAY = 800; // 800ms delay before closing

// Sidebar tab state - which section is currently active
const activeSidebarTab = ref("routing"); // "routing", "layers", "statistics", or "settings"

// Computed section title based on active tab
const sectionTitle = computed(() => {
  const titles = {
    routing: "Routing",
    layers: "Layers",
    statistics: "Stats",
    settings: "Settings",
  };
  return titles[activeSidebarTab.value] || "Lumo Pro";
});

// Computed section hint/instruction text based on active tab
const sectionHint = computed(() => {
  const hints = {
    routing: "Select hubs to plan your route",
    layers: "Choose a layer to visualize on the map",
    statistics: "View statistics and legend information",
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

// Legend drag state
const legendDraggedOut = ref(false);
const legendPosition = ref({ x: 100, y: 100 });
const legendSize = ref({ width: 280, height: 280 });
const legendOverBox = ref(false);
const legendBoxRef = ref(null);

function handleLegendDragOut() {
  legendDraggedOut.value = true;
}

function handleLegendClose() {
  legendDraggedOut.value = false;
  legendPosition.value = { x: 100, y: 100 }; // Reset position
  legendSize.value = { width: 280, height: 280 }; // Reset size
  legendOverBox.value = false;
}

function handleLegendPositionUpdate(position) {
  legendPosition.value = position;

  // Check if legend is over the box (only when dragged out and being moved)
  if (legendBoxRef.value && legendDraggedOut.value) {
    const boxRect = legendBoxRef.value.getBoundingClientRect();
    const legendWidth = legendSize.value.width;
    const legendHeight = legendSize.value.height;
    const legendCenterX = position.x + legendWidth / 2;
    const legendCenterY = position.y + legendHeight / 2;

    const isOverBox =
      legendCenterX >= boxRect.left &&
      legendCenterX <= boxRect.right &&
      legendCenterY >= boxRect.top &&
      legendCenterY <= boxRect.bottom;

    legendOverBox.value = isOverBox;
  } else {
    legendOverBox.value = false;
  }
}

function handleLegendDragBack() {
  if (legendOverBox.value) {
    legendDraggedOut.value = false;
    legendPosition.value = { x: 100, y: 100 };
    legendSize.value = { width: 280, height: 280 }; // Reset size
    legendOverBox.value = false;
  }
}

function handleLegendSizeUpdate(size) {
  legendSize.value = size;
}

// Map scale state
const mapZoom = ref(1.2);
const mapCenter = ref([0, 18]);
const scaleText = ref("1 km");
const locationText = ref("");
const zurichTime = ref("");
const isDaylight = ref(false);

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
  if (zoom >= 11) {
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
}

// Computed property to check if route can be planned
const canPlanRoute = computed(() => {
  return (
    api && startHub.value && endHub.value && startHub.value !== endHub.value
  );
});

// Trigger routing between hubs
async function route() {
  if (!canPlanRoute.value) return;

  if (api.drawRoute) {
    await api.drawRoute(startHub.value, endHub.value);
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

function focusZurich() {
  // Enable vibrancy layer by default when entering map from walkthrough
  vibrancyVisible.value = true;
  lightingVisible.value = false;
  combinedVisible.value = false;
  zurichFocusKey.value = Date.now();
}

function handleMapReady() {
  mapReady.value = true;
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
  top: 20px;
  left: 20px;
  bottom: 20px;
  width: 320px;
  padding: 0;
  background: #151517;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  z-index: 10;
  border-radius: 16px;

  display: flex;
  flex-direction: row; /* Changed to row to accommodate icon bar */
  justify-content: flex-start;

  transition:
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease,
    box-shadow 0.3s ease;
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
    opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s,
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s,
    visibility 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s; /* Smooth fade-in with slight delay */
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
  height: 20px;
  background: #ffffff;
  border-radius: 0 2px 2px 0;
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
  font-size: 28px;
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
  font-size: 14px;
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
  background: #151517;
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
  background: #1c1e21;
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
  background: #2a2f34;
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
  background: #151517;
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
    26,
    27,
    30,
    0.3
  ); /* Match icon bar color (#1a1b1e) with transparency */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  /* Inherit smooth transitions from .sidebar for width and padding */
  /* Additional transitions for background and box-shadow */
  transition:
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease,
    box-shadow 0.3s ease;
}

.sidebar--collapsed:hover {
  background: #1a1b1e; /* Solid icon bar color on hover */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
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

.sidebar--collapsed:hover {
  background: #1a1b1e; /* Solid icon bar color on hover */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
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

.route-select {
  width: 100%;
  padding: 14px 12px;
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
}

.route-input-content:has(.route-label-float--active) .route-select,
.route-input-content:has(.route-select:focus) .route-select {
  padding-top: 22px;
  padding-bottom: 6px;
}

.route-input-content:has(.route-select:focus) .route-label-float {
  top: 10px;
  transform: translateY(0);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.route-select:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.route-select:focus {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
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

.route-plan-btn svg {
  flex-shrink: 0;
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

/* -------- MAP SCALE -------- */
.map-scale {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 12;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  pointer-events: none;
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 0.4s ease,
    transform 0.4s ease;
}

.map-scale--visible {
  opacity: 1;
  transform: translateY(0);
}

.scale-line {
  width: 80px;
  height: 7px;
  background: rgba(255, 255, 255, 0.8);
  border-top: 1px solid rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(0, 0, 0, 0.3);
}

.scale-label {
  font-size: 18px;
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
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* -------- MAP CITY BUTTON -------- */
.map-city-button {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 12;
  width: 56px;
  height: 56px;
  border-radius: 8px;
  background: rgba(21, 21, 23, 0.3);
  border: none;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition:
    opacity 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    transform 0.4s cubic-bezier(0.16, 0.84, 0.24, 1),
    visibility 0ms 0.4s,
    background 0.15s ease;
  pointer-events: none;
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
  width: 20px;
  height: 20px;
  display: block;
  flex-shrink: 0;
}

/* -------- MAP LOCATION -------- */
.map-location {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 12;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  pointer-events: none;
  opacity: 0;
  transform: translateY(-10px);
  transition:
    opacity 0.4s ease,
    transform 0.4s ease;
}

.map-location--visible {
  opacity: 1;
  transform: translateY(0);
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
  margin-top: 16px;
}

.legend-box-new {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 16px;
  background: linear-gradient(180deg, #1a1b1e 0%, #141517 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-sizing: border-box;
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3);
  transition:
    background 0.2s ease,
    border-color 0.2s ease;
}

.legend-box-new--highlight {
  background: linear-gradient(180deg, #2a2b2e 0%, #242527 100%);
  border-color: rgba(255, 255, 255, 0.2);
}

.legend-box-empty {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.legend-box-empty svg {
  opacity: 0.5;
}

.legend-box-empty-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  text-align: center;
}
</style>

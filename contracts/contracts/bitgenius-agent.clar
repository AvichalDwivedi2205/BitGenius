;; BitGenius Agent Smart Contract
;; Handles agent creation, management, logging and performance metrics

(define-constant ERR-UNAUTHORIZED (err u403))
(define-constant ERR-NOT-FOUND (err u404))
(define-constant ERR-INVALID-PARAMS (err u400))
(define-constant ERR-INSUFFICIENT-FUNDS (err u402))

(define-constant STATUS-ONLINE "online")
(define-constant STATUS-IDLE "idle")
(define-constant STATUS-STOPPED "stopped")

;; Maps for agent templates, agents, logs, metrics, and user settings
(define-map agent-templates 
  { template-id: (string-ascii 20) }
  {
    description: (string-ascii 100),
    default-strategy: (string-ascii 100)
  }
)

(define-map agents 
  { agent-id: uint }
  {
    owner: principal,
    name: (string-ascii 50),
    agent-type: (string-ascii 20),
    strategy: (string-ascii 100),
    status: (string-ascii 20),
    trigger-condition: (string-ascii 100),
    privacy-enabled: bool,
    allocation: uint,
    created-at: uint,
    last-active: uint
  }
)

(define-data-var agent-id-counter uint u0)

(define-map logs 
  { agent-id: uint, timestamp: uint }
  {
    action: (string-ascii 50),
    status: (string-ascii 20),
    transaction-id: (optional (buff 32)),
    amount: (optional uint),
    fee: (optional uint),
    details: (string-ascii 200)
  }
)

(define-map performance-metrics 
  { agent-id: uint, period: uint }
  {
    actions-count: uint,
    success-count: uint,
    failure-count: uint,
    total-fees: uint,
    total-volume: uint
  }
)

(define-map user-settings 
  { user: principal }
  {
    default-agent-type: (string-ascii 20),
    privacy-default: bool,
    notification-level: (string-ascii 20),
    execution-mode: (string-ascii 20),
    runtime-cap: uint
  }
)

;; Initialize agent templates
(map-set agent-templates 
  { template-id: "auto_dca" }
  {
    description: "Automated dollar-cost averaging for Bitcoin",
    default-strategy: "Buy BTC at regular intervals regardless of price to reduce volatility impact"
  }
)

(map-set agent-templates 
  { template-id: "privacy_mixer" }
  {
    description: "Privacy-focused transaction management",
    default-strategy: "Utilize Rebar Shield for enhanced transaction privacy and metadata protection"
  }
)

(map-set agent-templates 
  { template-id: "arbitrage_hunter" }
  {
    description: "Profit from price differences across exchanges",
    default-strategy: "Monitor multiple exchanges for price differentials and execute trades when profitable"
  }
)

(map-set agent-templates 
  { template-id: "treasury_tracker" }
  {
    description: "Monitor and manage Bitcoin treasury operations",
    default-strategy: "Track treasury positions and provide alerts for key metrics and thresholds"
  }
)

(define-public (register-agent 
  (name (string-ascii 50))
  (agent-type (string-ascii 20))
  (strategy (string-ascii 100))
  (trigger-condition (string-ascii 100))
  (privacy-enabled bool)
  (allocation uint)
)
  (let
    (
      (new-id (+ (var-get agent-id-counter) u1))
      (now block-height)
      (template (map-get? agent-templates { template-id: agent-type }))
    )
    (begin
      (asserts! (is-some template) ERR-INVALID-PARAMS)
      
      (map-set agents 
        { agent-id: new-id }
        {
          owner: tx-sender,
          name: name,
          agent-type: agent-type,
          strategy: strategy,
          status: STATUS-ONLINE,
          trigger-condition: trigger-condition,
          privacy-enabled: privacy-enabled,
          allocation: allocation,
          created-at: now,
          last-active: now
        }
      )
      
      (map-set performance-metrics 
        { agent-id: new-id, period: now }
        {
          actions-count: u0,
          success-count: u0,
          failure-count: u0,
          total-fees: u0,
          total-volume: u0
        }
      )
      
      (var-set agent-id-counter new-id)
      (ok new-id)
    )
  )
)

(define-public (log-agent-action
  (agent-id uint)
  (action (string-ascii 50))
  (status (string-ascii 20))
  (transaction-id (optional (buff 32)))
  (amount (optional uint))
  (fee (optional uint))
  (details (string-ascii 200))
)
  (let 
    ((now block-height)
     (agent (unwrap! (map-get? agents { agent-id: agent-id }) ERR-NOT-FOUND))
     (period (/ now u144)))
    
    (asserts! (is-eq tx-sender (get owner agent)) ERR-UNAUTHORIZED)
    
    (map-set logs 
      { agent-id: agent-id, timestamp: now }
      {
        action: action,
        status: status,
        transaction-id: transaction-id,
        amount: amount,
        fee: fee,
        details: details
      }
    )
    
    (map-set agents { agent-id: agent-id } (merge agent { last-active: now }))
    
    (match (map-get? performance-metrics { agent-id: agent-id, period: period })
      metrics 
      (map-set performance-metrics 
        { agent-id: agent-id, period: period }
        {
          actions-count: (+ (get actions-count metrics) u1),
          success-count: (if (is-eq status "success") (+ (get success-count metrics) u1) (get success-count metrics)),
          failure-count: (if (is-eq status "failure") (+ (get failure-count metrics) u1) (get failure-count metrics)),
          total-fees: (+ (get total-fees metrics) (default-to u0 fee)),
          total-volume: (+ (get total-volume metrics) (default-to u0 amount))
        }
      )
      (map-set performance-metrics 
        { agent-id: agent-id, period: period }
        {
          actions-count: u1,
          success-count: (if (is-eq status "success") u1 u0),
          failure-count: (if (is-eq status "failure") u1 u0),
          total-fees: (default-to u0 fee),
          total-volume: (default-to u0 amount)
        }
      )
    )
    (ok true)
  )
)

(define-public (update-agent-status 
  (agent-id uint) 
  (new-status (string-ascii 20))
)
  (let ((agent (unwrap! (map-get? agents { agent-id: agent-id }) ERR-NOT-FOUND)))
    (asserts! (is-eq tx-sender (get owner agent)) ERR-UNAUTHORIZED)
    
    (asserts! (or 
      (is-eq new-status STATUS-ONLINE) 
      (is-eq new-status STATUS-IDLE) 
      (is-eq new-status STATUS-STOPPED)) 
      ERR-INVALID-PARAMS)
    
    (map-set agents { agent-id: agent-id } (merge agent { status: new-status }))
    (ok true)
  )
)

(define-public (update-agent-strategy
  (agent-id uint)
  (new-strategy (string-ascii 100))
)
  (let ((agent (unwrap! (map-get? agents { agent-id: agent-id }) ERR-NOT-FOUND)))
    (asserts! (is-eq tx-sender (get owner agent)) ERR-UNAUTHORIZED)
    
    (map-set agents { agent-id: agent-id } (merge agent { strategy: new-strategy }))
    (ok true)
  )
)

(define-public (update-agent-trigger
  (agent-id uint)
  (new-trigger (string-ascii 100))
)
  (let ((agent (unwrap! (map-get? agents { agent-id: agent-id }) ERR-NOT-FOUND)))
    (asserts! (is-eq tx-sender (get owner agent)) ERR-UNAUTHORIZED)
    
    (map-set agents { agent-id: agent-id } (merge agent { trigger-condition: new-trigger }))
    (ok true)
  )
)

(define-public (update-agent-privacy
  (agent-id uint)
  (privacy-enabled bool)
)
  (let ((agent (unwrap! (map-get? agents { agent-id: agent-id }) ERR-NOT-FOUND)))
    (asserts! (is-eq tx-sender (get owner agent)) ERR-UNAUTHORIZED)
    
    (map-set agents { agent-id: agent-id } (merge agent { privacy-enabled: privacy-enabled }))
    (ok true)
  )
)

(define-public (update-agent-allocation
  (agent-id uint)
  (new-allocation uint)
)
  (let ((agent (unwrap! (map-get? agents { agent-id: agent-id }) ERR-NOT-FOUND)))
    (asserts! (is-eq tx-sender (get owner agent)) ERR-UNAUTHORIZED)
    
    (map-set agents { agent-id: agent-id } (merge agent { allocation: new-allocation }))
    (ok true)
  )
)

(define-public (save-user-settings
  (default-agent-type (string-ascii 20))
  (privacy-default bool)
  (notification-level (string-ascii 20))
  (execution-mode (string-ascii 20))
  (runtime-cap uint)
)
  (begin
    (asserts! (is-some (map-get? agent-templates { template-id: default-agent-type })) ERR-INVALID-PARAMS)
    
    (map-set user-settings 
      { user: tx-sender }
      {
        default-agent-type: default-agent-type,
        privacy-default: privacy-default,
        notification-level: notification-level,
        execution-mode: execution-mode,
        runtime-cap: runtime-cap
      }
    )
    (ok true)
  )
)

(define-read-only (get-agent-by-id (agent-id uint))
  (map-get? agents { agent-id: agent-id })
)

(define-read-only (is-owner-of-agent (owner principal) (agent-id uint))
  (match (map-get? agents { agent-id: agent-id })
    agent (is-eq owner (get owner agent))
    false
  )
)

(define-read-only (get-most-recent-log (agent-id uint))
  (map-get? logs { agent-id: agent-id, timestamp: block-height })
)

(define-read-only (get-log (agent-id uint) (timestamp uint))
  (map-get? logs { agent-id: agent-id, timestamp: timestamp })
)

(define-read-only (get-agent-performance (agent-id uint) (period uint))
  (map-get? performance-metrics { agent-id: agent-id, period: period })
)

(define-read-only (get-agent-status (agent-id uint))
  (match (map-get? agents { agent-id: agent-id })
    agent (some (get status agent))
    none
  )
)

(define-read-only (get-user-settings (user principal))
  (map-get? user-settings { user: user })
)

(define-read-only (get-agent-template (template-id (string-ascii 20)))
  (map-get? agent-templates { template-id: template-id })
)

(define-read-only (get-all-templates)
  (list "auto_dca" "privacy_mixer" "arbitrage_hunter" "treasury_tracker")
)

(define-read-only (get-agent-count)
  (var-get agent-id-counter)
)

(define-read-only (is-agent-owner (agent-id uint) (user principal))
  (match (map-get? agents { agent-id: agent-id })
    agent (is-eq user (get owner agent))
    false
  )
)
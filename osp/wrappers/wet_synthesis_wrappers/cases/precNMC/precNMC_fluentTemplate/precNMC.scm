
;PLANE. Create planes to see results.
(define create-plane-line
  (lambda (arg)
    (for-each
      (lambda (name method value)
        (ti-menu-load-string
          (format #f "surface plane-surface ~a ~a ~a quit" name method value))
        (newline))
      '(yz-x0 zx-y0 )
      '(yz-plane zx-plane)
      '(0.0 0.0))))

;DISCRETIZATION SCHEME. Set the order of discretization scheme
(define schemeorder-flow
  (lambda (variables schemes)
    (for-each
      (lambda (variable scheme)
        (ti-menu-load-string
          (format #f "solve set discretization-scheme ~a ~a" variable scheme))
        (newline))
      variables schemes)))

(define schemeorder
  (lambda (order udsindex)
    (for-each
      (lambda (index)
        (ti-menu-load-string
          (format #f "solve set discretization-scheme uds-~a ~a" index order))
        (newline))
      udsindex)))

;UNDER-RELAXATION. Set the under-relaxation factors
(define relaxfactor-flow
  (lambda (variables relax-factors)
    (for-each
      (lambda (variable relax-factor)
        (ti-menu-load-string
          (format #f "solve set under-relaxation ~a ~a" variable relax-factor))
        (newline))
      variables relax-factors)))

(define relaxfactor
  (lambda (rf udsindex)
    (for-each
      (lambda (index)
        (ti-menu-load-string
          (format #f "solve set under-relaxation uds-~a ~a" index rf))
        (newline))
      udsindex)))

;SOURCE TERM. Set the source for the UDS. If we want to activate the source we have to write
;"1 no yes and the name of the source (conc or mom)", otherwise we have to write "0"
(define sourceterm
  (lambda (selection)
    (cond ( (equal? selection "none")
            (ti-menu-load-string
              (format #f
                (string-append
                  (do ((str "define boundary-conditions fluid fluid-1 no yes 0 0 0 0 0 0\n") (i 0 (+ i 1))) ((= i 9) str)
                      (define str (string-append str "0\n")))
                  "no no no 0. no 0. no 0. no 0 no 0 no 1 no no no no no\n"))))
          ( (equal? selection "species")
            (ti-menu-load-string
              (format #f
                (string-append
                  (do ((str "define boundary-conditions fluid fluid-1 no yes 0 0 0 0 0 0\n") (i 0 (+ i 1))) ((= i 3) str)
                      (define str (string-append str "1 no yes \"conc_source::libudf\"\n")))
                  "0\n 0\n"
                  (do ((str "") (i 0 (+ i 1))) ((= i 4) str)
                      (define str (string-append str "0\n")))
                  "no no no 0. no 0. no 0. no 0 no 0 no 1 no no no no no\n"))))
          ( (equal? selection "moments")
            (ti-menu-load-string
              (format #f
                (string-append
                  (do ((str "define boundary-conditions fluid fluid-1 no yes 0 0 0 0 0 0\n") (i 0 (+ i 1))) ((= i 5) str)
                      (define str (string-append str "0\n")))
                  (do ((str "") (i 0 (+ i 1))) ((= i 4) str)
                      (define str (string-append str "1 no yes \"mom_source::libudf\"\n")))
                  "no no no 0. no 0. no 0. no 0 no 0 no 1 no no no no no\n"))))
          ( (equal? selection "all")
            (ti-menu-load-string
              (format #f
                (string-append
                  (do ((str "define boundary-conditions fluid fluid-1 no yes 0 0 0 0 0 0\n") (i 0 (+ i 1))) ((= i 3) str)
                      (define str (string-append str "1 no yes \"conc_source::libudf\"\n")))
                  "0\n 0\n"
                  (do ((str "") (i 0 (+ i 1))) ((= i 4) str)
                      (define str (string-append str "1 no yes \"mom_source::libudf\"\n")))
                  "no no no 0. no 0. no 0. no 0 no 0 no 1 no no no no no\n")))))))

;USER-DEFINED SCALARS AND MEMORIES. Allocate UDS and UDM
(define allocate-memory
  (lambda (nUDS nUDM)
    (for-each
      (lambda (type number options)
        (ti-menu-load-string
          (format #f "define user-defined ~a ~a ~a" type number options)))
      '(user-defined-scalars user-defined-memory)
      (list nUDS nUDM)
      (list
        (do ((str "no no\n") (i 0 (+ i 1))) ((= i nUDS) str)
            (define str (string-append str "yes\n\"mass flow rate\"\n")))
        "\n"))))

;USER-DEFINED FUNCTION. Compile the udf
(define compile-udf
  (lambda (OS)
    (cond ( (equal? OS "Linux")
            (ti-menu-load-string
              (format #f
                (string-append
                  "define user-defined compiled-functions compile libudf yes "
                  "precNMC_adjust.c precNMC_sources.c\n \n"
                  "headerFiles/chemicalEquilibria.h headerFiles/defMacros.h headerFiles/externFuncs.h "
                  "headerFiles/externVars.h headerFiles/momentCalc.h headerFiles/particleProcesses.h"))))
          ( (equal? OS "Windows")
            (ti-menu-load-string
              (format #f
                (string-append
                  "define user-defined compiled-functions compile libudf yes\n"
                  "precNMC_adjust.c precNMC_sources.c\n \n"
                  "headerFiles/chemicalEquilibria.h headerFiles/defMacros.h "
                  "headerFiles/externVars.h headerFiles/momentCalc.h headerFiles/particleProcesses.h")))))))

(define setparameters
  (lambda (names values)
    (for-each
      (lambda (name value)
        (if (not (rp-var-object name))
          (rp-var-define name value 'real #f)
          (rpsetvar name value))
        (newline))
      names
      values)))

(define set-moving-zones
  (lambda (moving-zones stationary-zone-id)
    (for-each
      (lambda (moving-zone)
        (ti-menu-load-string
          (format #f
            (string-append
              "define boundary-conditions fluid ~a yes water no no yes ~a no ~a "
              "no 0.0 no 0.0 no 0.0 no 0.0 no 0.0 no 0.0 no 0.0 no 0.0 no 1.0 none no no no no no")
            moving-zone stationary-zone-id impeller-angular-velocity))
        (newline))
      moving-zones)))

(define initialize-precNMC-flow
  (lambda (arg)

    ;BOUNDARY
    ;Velocity-inlet.
    ;The numeric values are VELOCITY, GAUGE PRESSURE, TURBULENCE INTENSITY, HYDRAULIC DIAMETER
    (for-each
      (lambda (name vel turb-intensity hd)
        (ti-menu-load-string
          (format #f
            (string-append
              "define boundary-conditions velocity-inlet ~a no no yes yes no ~a no 0. no "
              "yes ~a ~a")
            name vel turb-intensity hd))
        (newline))
      '(inlet-metals inlet-nh3 inlet-naoh)
      '(flowrate-metals flowrate-nh3 flowrate-naoh)
      (make-list 3 inlet-turb-intensity)
      (make-list 3 inlet-hydraulic-diameter))

    ;Pressure-outlet. The numeric values are GAUGE PRESSURE, TURBULENCE INTENSITY, HYDRAULIC DIAMETER
    (ti-menu-load-string
      (format #f
        (string-append
          "define boundary-conditions pressure-outlet outlet yes no 0. no yes no yes 0.5 0.01 "
          "yes no no no") outlet-pressure outlet-turb-intensity outlet-hydraulic-diameter))
    (newline)

    ;Walls
    (for-each
      (lambda (name rotational-vel)
        (ti-menu-load-string
          (format #f
            (string-append
              "define boundary-conditions wall ~a yes motion-bc-moving no yes yes no "
              "no 0.0 no 0.5 no ~a 0.0 0.0 0.0 0.0 0.0 1.0")
            name rotational-vel))
        (newline))
      '(inlet1wall pitchbladewalls rushtonwalls injectionpipeswalls liquidvolume:1 connectingtube overflowwalls reactorwalls shaft_ )
      '(0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 impeller-angular-velocity))

    ;SCHEME. Select SIMPLE algorithm
    (ti-menu-load-string
      (format #f "solve set p-v-coupling 20"))
    (newline)

    (schemeorder-flow '(pressure mom k epsilon) '(10 0 0 0))
    (relaxfactor-flow '(pressure mom k epsilon turb-viscosity) '(0.3 0.1 0.1 0.1 0.1))

    ;EQUATIONS. Set equations to solve
    (for-each
      (lambda (variable flag)
        (ti-menu-load-string
          (format #f "solve set equations ~a ~a" variable flag))
        (newline))
      '(flow ke)
      '(yes yes))

    ;CONVERGENCE-CRITERIA. Set convergence criteria
    (newline)
    (ti-menu-load-string
      (format #f
        (do ((str "solve monitors residual convergence-criteria\n") (i 0 (+ i 1))) ((= i 6) str)
            (define str (string-append str "1e-6\n")))))

    ;INITIAL VALUES
    (for-each
      (lambda (variable value)
        (ti-menu-load-string
          (format #f "solve initialize set-defaults ~a ~a" variable value))
        (newline))
      '(pressure x-velocity y-velocity z-velocity k epsilon)
      '(initial-p initial-Ux initial-Uy initial-Uz initial-k initial-epsilon))

    ;INITIALIZATION
    (ti-menu-load-string
      (format #f "solve initialize initialize-flow"))
    (newline)

    ))

(define initialize-precNMC
  (lambda (arg)
    ;CUSTOM FIELD FUNCTION. Define the custom field function to patch the udm-21
    (ti-menu-load-string
      (format #f "define custom-field-functions define \"diss-rate\" \"turb_diss_rate\" "))

    ;Allocate the required number of UDS and UDM
    (allocate-memory 9 22)

    ;Compile udf
    (compile-udf "Linux")

    ;USER-DEFINED UDF. Load the library and hook adjust function
    (for-each
      (lambda (type options)
        (ti-menu-load-string
          (format #f "define user-defined ~a ~a" type options)))
      '("compiled-functions load" "function-hooks adjust")
      '("\"libudf\"\n" "\n\"adjust::libudf\"\n"))

    ;DIFFUSIVITY. Set UDS diffusivity (0 for the moments)
    (ti-menu-load-string
      (format #f
        (string-append
          (do ((str "define materials change-create water-liquid water-liquid no no no no no no yes defined-per-uds\n") (i 0 (+ i 1))) ((= i 5) str)
              (define str (string-append str (format #f "~a user-defined \"conc_diffusivity::libudf\"\n" i))))
          (do ((str "") (i 5 (+ i 1))) ((= i 9) str)
              (define str (string-append str (format #f "~a constant 0\n" i))))
          "-1 no \n")))

    ; SCHEME. Select SIMPLE algorithm
    (ti-menu-load-string
      (format #f "solve set p-v-coupling 20"))
    (newline)

    ;EQUATIONS. Set equations to solve
    (for-each
      (lambda (variable flag)
        (ti-menu-load-string
          (format #f "solve set equations ~a ~a" variable flag))
        (newline))
      '(flow kw)
      '(no no))

    (do ((i 0 (+ i 1))) ((> i 8))
      (ti-menu-load-string
        (format #f "solve set equations uds-~a yes" i))
        (newline))

    ;CONVERGENCE-CRITERIA. Set convergence criteria
    (newline)
    (ti-menu-load-string
      (format #f
        (do ((str "solve monitors residual convergence-criteria\n") (i 0 (+ i 1))) ((= i 9) str)
            (define str (string-append str "1e-15\n")))))

    ;Set scheme order
    (schemeorder 0 '(0 1 2 3 4 5 6 7 8))

    ;Set the under-relaxation factor
    (relaxfactor 1e-5 '(0 1 2 3 4 5 6 7 8))

    ;BOUNDARY
    ;Velocity-inlet.
    ;The numeric values are VELOCITY, GAUGE PRESSURE, TURBULENCE INTENSITY, HYDRAULIC DIAMETER,
    ;the concentrations and UDS 5, 6, 7, 8
    (for-each
      (lambda (inlet vel turb-intensity hd tot-ni tot-mn tot-co tot-nh3 inert-charge)
        (ti-menu-load-string
          (format #f "define boundary-conditions velocity-inlet ~a no no yes yes no ~a no 0. no no no yes ~a ~a no yes no yes no yes no yes no yes no yes no yes no yes no yes no ~a no ~a no ~a no ~a no ~a no 0. no 0. no 0. no 0. "
            inlet vel turb-intensity hd tot-ni tot-mn tot-co tot-nh3 inert-charge))
        (newline))
      '(inlet1 inlet2 inlet3 inlet4)
      (make-list 4 0.33953054526271)
      (make-list 4 7.727)
      (make-list 4 0.001)
      '(0.16 0 0 0)
      '(0.02 0 0 0)
      '(0.02 0 0 0)
      '(0 0.2 0 0)
      '(-0.4 0 0.2 0.2))

    ;BOUNDARY
    ;Pressure-outlet. The numeric values are GAUGE PRESSURE, TURBULENCE INTENSITY, HYDRAULIC DIAMETER and the UDS 0-8
    (ti-menu-load-string
      (format #f "define boundary-conditions pressure-outlet outlet yes no 0. no yes no no no yes 7.086 0.002 yes yes yes yes yes yes yes yes yes no 0 no 0 no 0 no 0 no 0 no 0 no 0 no 0 no 0 yes no no no" ))

    ;Activate source terms
    (sourceterm "all")

    ;PATCH
    (for-each
      (lambda (index value)
        (ti-menu-load-string
          (format #f "solve patch (fluid-1) () uds-~a no ~a" index value))
        (newline))
      '(0 1 2 3 4 5 6 7 8)
      '(1.6e-05 2e-06 2e-06 2e-05 2e-05 1786.535 1.786535e-05 1.826732e-13 1.909859e-21))


    (do ((i 0 (+ i 1))) ((> i 20))
      (ti-menu-load-string
        (format #f "solve patch (fluid-1) () udm-~a no 0 " i))
      (newline))

    (for-each
      (lambda (region index value)
        (ti-menu-load-string
          (format #f "solve patch () (~a) uds-~a no ~a " region index value))
        (newline))
      '(region_metal region_metal region_metal region_nh3 region_oh region_metal)
      '(0 1 2 3 4 4)
      '(0.16 0.02 0.02 0.2 0.2 -0.4))

    (ti-menu-load-string (format #f "solve patch (fluid-1) () udm-21 yes diss-rate "))
    (newline)

    (ti-menu-load-string (format #f "solve patch () (region_0) udm-20 no 1.0 "))))

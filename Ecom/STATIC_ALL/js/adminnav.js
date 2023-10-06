    var trriger = gsap.matchMedia();

    gsap.registerPlugin(ScrollTrigger);
    ScrollTrigger.create({
        trigger: ".bodysection",
        pin: ".navsection",
        pinSpacing: false,

        start: "top top",

        end: "bottom bottom",
    });

    trriger.add(
        { ismobile: "(max-width: 990px)", islap: "(min-width: 990px)" },
        (context) => {
          if (context.conditions.islap) {
            ScrollTrigger.enable();
          }
          if (context.conditions.ismobile) {
            ScrollTrigger.disable();
          }
        }
    );


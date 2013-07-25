/* jshint nonew: false */

var jarvis = jarvis || angular.module('jarvis', []);

jarvis.controller('WattmeterCtrl', ['$scope',
  function ($scope) {
    'use strict';

    var graph = null;

    var initGraph = function (element, value) {
      var labels = Object.keys(value).map(function (name) {
        return {
          name: name
        };
      });
      var series = new Rickshaw.Series.FixedDuration(
        labels,
        new Rickshaw.Color.Palette({
          scheme: 'spectrum14'
        }), {
          timeInterval: 5000,
          maxDataPoints: 100,
          timeBase: new Date().getTime() / 1000
        }
      );
      graph = new Rickshaw.Graph({
        element: element,
        width: 586,
        height: 400,
        renderer: 'line',
        stroke: true,
        series: series
      });
      new Rickshaw.Graph.Legend({
        element: document.querySelector('#legend-pm'),
        graph: graph
      });
      new Rickshaw.Graph.Axis.Y({
        element: document.querySelector('#y-axis-pm'),
        graph: graph,
        orientation: 'left',
        ticks: 5,
        tickFormat: function (n) {
          return n + ' Wh';
        }
      });
      graph.renderer.unstack = true;
      graph.render();
    };

    $scope.$on('wattmeter', function (ev, body) {
      if (graph === null) {
        var element = document.querySelector('#chart-pm');
        if (element !== null) {
          initGraph(element, body.value);
        }
      } else {
        graph.series.addData(body.value);
        graph.render();
      }
    });
  }
]);

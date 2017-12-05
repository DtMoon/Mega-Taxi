//
//  MegaTaxiTripCostViewController.swift
//  MegaTaxi
//
//  Created by Lingyun Gao on 21/11/2017.
//  Copyright © 2017 MegaTaxiCompany. All rights reserved.
//

import UIKit
import GoogleMaps
import GooglePlaces
import GooglePlacePicker
import SwiftSocket
import Foundation

class MegaTaxiTripCostViewController: UIViewController {
    
    private var locationManager = CLLocationManager()
    private enum Location {
        case originLocation
        case destinationLocation
    }
    private var whichLocation = Location.originLocation
    private var originLocationCoordinate: CLLocationCoordinate2D?
    private var destinationLocationCoordinate: CLLocationCoordinate2D?
    private var middleMarker: GMSMarker?
    private var duration = "21 min"
    private var cost = "30.00$"
    
    @IBOutlet weak var googleMapView: GMSMapView!
    
    @IBOutlet weak var originText: UIButton!
    
    @IBOutlet weak var destinationText: UIButton!
    
    @IBAction func originAutoComplete(_ sender: UIButton) {
        let autocompleteController = GMSAutocompleteViewController()
        autocompleteController.delegate = self
        whichLocation = Location.originLocation
        present(autocompleteController, animated: true, completion: nil)
    }
    
    @IBAction func destinationAutoComplete(_ sender: UIButton) {
        let autocompleteController = GMSAutocompleteViewController()
        autocompleteController.delegate = self
        whichLocation = Location.destinationLocation
        present(autocompleteController, animated: true, completion: nil)
    }
    
    @IBAction func showPath(_ sender: UIButton) {
//        originLocationCoordinate = CLLocationCoordinate2D(latitude: 40.760, longitude: -73.986)
//        destinationLocationCoordinate = CLLocationCoordinate2D(latitude: 40.807, longitude: -73.964)
        if let origin = originLocationCoordinate, let destination = destinationLocationCoordinate {
            print(origin.latitude)
            print(destination.latitude)
            fetchCostAndTime(from: origin, to: destination)
        }
    }
    
    private func fetchCostAndTime(from origin: CLLocationCoordinate2D, to destination: CLLocationCoordinate2D) {
        let socket = TCPClient(address: "35.193.237.218", port: 38471)
        switch socket.connect(timeout: 1000) {
        case .success:
            switch socket.send(data: [UInt8]("\(origin.latitude),\(origin.longitude)|\(destination.latitude),\(destination.longitude)".utf8)) {
            case .success:
                if let data = socket.read(1024, timeout: 1000) {
                    print("success")
                    if let response = String(bytes: data, encoding: .utf8) {
                        print("response: \(response)")
                        let index = response.index(of: "|") ?? response.endIndex
                        duration = String(response[..<index])+" min"
                        cost = "$ " + String(response[response.index(after: index)...])
                        drawPath(from: origin, to: destination)
                    }
                } else {
                    print("nil data received")
                }
                
            case .failure(let error):
                print("error\(error)")
            }
        case .failure(let error):
            print("error\(error)")
        }
        socket.close()
    }
    
    private func drawPath(from origin: CLLocationCoordinate2D, to destination: CLLocationCoordinate2D){
        let url = URL(string: "http://maps.googleapis.com/maps/api/directions/json?origin=\(origin.latitude),\(origin.longitude)&destination=\(destination.latitude),\(destination.longitude)&sensor=false&mode=driving")

        URLSession.shared.dataTask(with: url!, completionHandler: { [weak self] (data, response, error) in
            if error != nil {
                print("error")
            } else {
                do {
                    let json = try JSONSerialization.jsonObject(with: data!, options:.allowFragments) as! [String : AnyObject]
                    let routes = json["routes"] as! NSArray
                
                    DispatchQueue.main.async {
                        self?.googleMapView.clear()
                        for route in routes {
                            let routeOverviewPolyline: NSDictionary = (route as! NSDictionary).value(forKey: "overview_polyline") as! NSDictionary
                            let points = routeOverviewPolyline.object(forKey: "points")
                            let path = GMSPath.init(fromEncodedPath: points! as! String)
                            let polyline = GMSPolyline(path: path)
                            polyline.strokeWidth = 5
                            polyline.strokeColor = UIColor(red:1.00, green:0.59, blue:0.00, alpha:1.0)
                            
                            let middle = (path?.coordinate(at: (path?.count())! / 2))!
                            self?.middleMarker = GMSMarker()
                            self?.middleMarker?.position = middle
                            self?.middleMarker?.opacity = 0
                            self?.middleMarker?.title = self?.duration
                            self?.middleMarker?.snippet = self?.cost
//                            middleMarker.icon = self?.textToImage(text: "\(duration)\n\(cost)", size: CGSize(width: 100, height: 100))
                            self?.middleMarker?.map = self?.googleMapView
                            self?.googleMapView.selectedMarker = self?.middleMarker!
                            
                            let bounds = GMSCoordinateBounds(path: path!)
                            self?.googleMapView!.animate(with: GMSCameraUpdate.fit(bounds, withPadding: 50.0))
                            
                            polyline.map = self?.googleMapView
                        }
                        
                        // Creates a marker in the center of the map.
                        let originMarker = GMSMarker()
                        originMarker.position = origin
                        originMarker.icon = GMSMarker.markerImage(with: .blue)
                        originMarker.opacity = 0.8
                        originMarker.isTappable = false
                        originMarker.map = self?.googleMapView
                        
                        // Creates a marker in the center of the map.
                        let destinationMarker = GMSMarker()
                        destinationMarker.position = destination
                        destinationMarker.opacity = 0.8
                        destinationMarker.isTappable = false
                        destinationMarker.map = self?.googleMapView
                    }
                } catch let error as NSError {
                    print("error:\(error)")
                }
            }
        }).resume()
    }
    
//    func textToImage(text: String, size: CGSize) -> UIImage {
//        let data = text.data(using: String.Encoding.utf8, allowLossyConversion: true)
//        let drawText = NSString(data: data!, encoding: String.Encoding.utf8.rawValue)
//
//        let textFontAttributes = [
//            NSAttributedStringKey.font: UIFont(name: "Helvetica Bold", size: 20)!,
//            NSAttributedStringKey.foregroundColor: UIColor.red,
//            ]
//
//        UIGraphicsBeginImageContextWithOptions(size, false, 0)
//        drawText?.draw(in: CGRect(x: 0, y: 0, width: size.width, height: size.height), withAttributes: textFontAttributes)
//        let newImage = UIGraphicsGetImageFromCurrentImageContext()
//        UIGraphicsEndImageContext()
//
//        return newImage!
//    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        locationManager = CLLocationManager()
        locationManager.delegate = self
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
        
        googleMapView.delegate = self
        googleMapView.isMyLocationEnabled = true
        googleMapView.settings.myLocationButton = true
        googleMapView.isUserInteractionEnabled = true

        middleMarker?.isTappable = false

        // Do any additional setup after loading the view.
    
    }
}

extension MegaTaxiTripCostViewController: GMSAutocompleteViewControllerDelegate {

    // Handle the user's selection.
    func viewController(_ viewController: GMSAutocompleteViewController, didAutocompleteWith place: GMSPlace) {
        print("Place name: \(place.name)")
        print("Place address: \(place.formattedAddress)")
        print("Place attributions: \(place.attributions)")
        switch whichLocation {
        case .originLocation:
            originLocationCoordinate = place.coordinate
            originText?.setTitle(place.name, for: .normal)
        case .destinationLocation:
            destinationLocationCoordinate = place.coordinate
            destinationText?.setTitle(place.name, for: .normal)
        }
        dismiss(animated: true, completion: nil)
    }

    func viewController(_ viewController: GMSAutocompleteViewController, didFailAutocompleteWithError error: Error) {
        // TODO: handle the error.
        print("Error: ", error.localizedDescription)
    }

    // User canceled the operation.
    func wasCancelled(_ viewController: GMSAutocompleteViewController) {
        dismiss(animated: true, completion: nil)
    }

    // Turn the network activity indicator on and off again.
    func didRequestAutocompletePredictions(_ viewController: GMSAutocompleteViewController) {
        UIApplication.shared.isNetworkActivityIndicatorVisible = true
    }

    func didUpdateAutocompletePredictions(_ viewController: GMSAutocompleteViewController) {
        UIApplication.shared.isNetworkActivityIndicatorVisible = false
    }
}

extension MegaTaxiTripCostViewController: CLLocationManagerDelegate {

    // Handle incoming location events.
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        if let location = locations.first {
            print("Location: \(location)")

            googleMapView.camera = GMSCameraPosition.camera(withLatitude: location.coordinate.latitude,
                                                  longitude: location.coordinate.longitude,
                                                  zoom: 17.0)
            locationManager.stopUpdatingLocation()
        }
    }

    // Handle location manager errors.
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        locationManager.stopUpdatingLocation()
        print("Error: \(error)")
    }
}

extension MegaTaxiTripCostViewController: GMSMapViewDelegate {
    
    func mapView(_ mapView: GMSMapView, didTapAt coordinate: CLLocationCoordinate2D) {
        googleMapView.selectedMarker = middleMarker
    }
}


import { useParams, useNavigate } from "react-router-dom";
import { useContext, useEffect, useState } from "react";
import ShelterTitle from "../../components/ShelterTitle";
import SideBySide from "../../components/SideBySide";
import Grid from "../../components/Grid";
import Card from "../../components/Card";
import { UserContext } from "../../contexts/UserContext";
import ConfrimDenyButton from "../../components/ConfirmDenyEditButtons";
import EditableReactCarousel from "../../components/EditableReactCarousel";
import EditablePetListingDetails from "../../components/EditablePetListingDetails";
import TextArea from "../../components/TextArea";
import ErrorModal from "../../components/ErrorModal";
import NotFound from "../NotFound";
const PetListingEditable = () => {
  const { pet_listing_id } = useParams();
  const navigate = useNavigate();
  const { user, token } = useContext(UserContext);

  const [petData, setPetData] = useState();
  const [shelterData, setShelterData] = useState();
  const [loadingData, setLoadingData] = useState(true);
  const [petImages, setPetImages] = useState([]);
  const [deletedPetImageIds, setDeletedPetImageIds] = useState([]);
  const [nextPetImageId, setNextPetImageId] = useState(0);

  const [showError, setShowError] = useState(false);
  const [errorObj, setErrorObj] = useState({
    title: "There was an issue updating your pet listing",
    body: "",
  });

  const [notFound, set404] = useState(false);

  const setNotFound = () => {
    set404(true);
    setLoadingData(false);
  };

  useEffect(() => {
    const onUploadedImageDelete = (currObj) => (images) => {
      setPetImages(images.filter((image) => image.id !== currObj.id));
      setDeletedPetImageIds((prev) => [...prev, currObj.id]);
    };
    const perfromUseEffect = async () => {
      const petResponse = await fetch(`/pet_listing/${pet_listing_id}`, {
        method: "GET",
        redirect: "follow",
        headers: {
          accept: "application/json",
        },
      });
      if (!petResponse.ok) {
        setNotFound(true);
        return;
      }
      const petJson = await petResponse.json();
      setPetData(petJson);
      const shelterResponse = await fetch(
        `/accounts/shelter/${petJson.shelter.id}`,
        {
          method: "GET",
          redirect: "follow",
          headers: {
            accept: "application/json",
          },
        }
      );
      if (!shelterResponse.ok) {
        setNotFound(true);
        return;
      }
      const shelterJson = await shelterResponse.json();
      setShelterData(shelterJson);
      if (user?.shelter?.id !== shelterJson.shelter.id) {
        setNotFound(true);
        return;
      }

      const petImagesResponse = await fetch(
        `/pet_listing/${pet_listing_id}/image`,
        {
          method: "GET",
          redirect: "follow",
          headers: {
            accept: "application/json",
          },
        }
      );
      if (!petImagesResponse.ok) {
        setNotFound(true);
        return;
      }
      const petImagesJson = await petImagesResponse.json();
      if (petImagesJson.length !== 0) {
        setNextPetImageId(petImagesJson[petImagesJson.length - 1].id + 1);
      } else {
        setNextPetImageId(0);
      }

      setPetImages(
        await Promise.all(
          petImagesJson
            .map(async (imageObj, i) => {
              // TODO: How to fix this?? I think this issue goes away
              // Once we upload using React.
              // Nope, it does not.
              const url = imageObj.image.replace("http://127.0.0.1:8000", "");
              const response = await fetch(url);
              if (!response.ok) {
                return "";
              }
              return {
                url: URL.createObjectURL(await response.blob()),
                id: imageObj.id,
                onDelete: onUploadedImageDelete(imageObj),
              };
            })
            .reverse()
        )
      );

      setLoadingData(false);
    };
    perfromUseEffect();
  }, [navigate, pet_listing_id, user]);

  const addNewImage = (image) => {
    setPetImages([
      {
        url: URL.createObjectURL(image),
        id: nextPetImageId,
        onDelete: (images) => {
          setPetImages(images.filter((image) => image.id !== nextPetImageId));
        },
        file: image,
      },
      ...petImages,
    ]);
    setNextPetImageId(nextPetImageId + 1);
  };

  const errorCheck = () => {
    let error = false;
    const setMsg = (msg) => {
      setErrorObj({
        ...errorObj,
        body: msg,
      });
      error = true;
      setShowError(true);
    };

    if (petImages.length === 0) {
      setMsg("You must include at least one image for your gallery");
    }
    if (petData.pet_name === "" || petData.pet_name.length > 50) {
      setMsg("The pet named you entered is invalid");
    }
    if (petData.breed === "" || petData.breed.length > 50) {
      setMsg("The pet breed you entered is invalid");
    }
    if (petData.medical_history === "") {
      setMsg("You must include a medical history");
    }
    if (petData.requirements === "") {
      setMsg("You must include requirements");
    }
    if (petData.additional_comments === "") {
      setMsg("You must include additional comments");
    }
    return error;
  };

  const uploadPetData = async () => {
    if (errorCheck()) {
      return;
    }

    await fetch(`/pet_listing/${pet_listing_id}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(petData),
    });

    await Promise.all(
      petImages
        .filter((image) => !!image.file)
        .map((image) => {
          const imagePostBody = new FormData();
          imagePostBody.append("image", image.file);
          return fetch(`/pet_listing/${pet_listing_id}/image/`, {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
            body: imagePostBody,
          });
        })
    );

    await Promise.all(
      deletedPetImageIds.map((id) => {
        return fetch(`/pet_listing/${pet_listing_id}/image/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      })
    );

    navigate(`/pet_listing/${pet_listing_id}`);
  };

  const updateParam = (field, value) => {
    setPetData({ ...petData, [field]: value });
  };

  return loadingData ? (
    <></>
  ) : notFound ||
    !user ||
    !user.shelter ||
    user.shelter.id !== shelterData.shelter.id ? (
    <NotFound></NotFound>
  ) : (
    <div className="flex flex-col items-center justify-center min-h-screen py-3 bg-gray-50">
      <ConfrimDenyButton
        onConfirm={uploadPetData}
        onDeny={() => navigate(`/pet_listing/${pet_listing_id}`)}
      />
      <ErrorModal
        errorObj={errorObj}
        show={showError}
        setShow={setShowError}
      ></ErrorModal>
      <ShelterTitle shelterData={shelterData} link={true} />
      <section id="pet_gallery" className="w-5/6 p-2 mb-3 sm:w-3/4">
        <SideBySide>
          <EditableReactCarousel images={petImages} addNewImage={addNewImage} />
          <EditablePetListingDetails
            petData={petData}
            updateParam={updateParam}
          />
        </SideBySide>
      </section>
      <section id="pet_history" className="w-5/6 sm:w-3/4 bg-50">
        <Grid cols={2}>
          <Card title={"Medical History"}>
            <TextArea
              title={"Medical History"}
              rows={4}
              onChange={(value) => {
                updateParam("medical_history", value);
              }}
              value={petData.medical_history}
            ></TextArea>
          </Card>
          <Card title={"Requirements"}>
            <TextArea
              title={"Requirements"}
              rows={4}
              onChange={(value) => {
                updateParam("requirements", value);
              }}
              value={petData.requirements}
            ></TextArea>
          </Card>
        </Grid>
        <Grid cols={1}>
          <Card title={"Additional Comments"}>
            <TextArea
              title={"Additional Comments"}
              rows={4}
              onChange={(value) => {
                updateParam("additional_comments", value);
              }}
              value={petData.additional_comments}
            ></TextArea>
          </Card>
        </Grid>
      </section>
    </div>
  );
};

export default PetListingEditable;

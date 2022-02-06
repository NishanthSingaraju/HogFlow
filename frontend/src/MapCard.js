import { Card, CardContent } from '@mui/material';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

function MapCard({children}){
    return (
      <Card className="card_map">
          <CardContent>
                {children}
            </CardContent>
        </Card>
    )
  }

  export default MapCard